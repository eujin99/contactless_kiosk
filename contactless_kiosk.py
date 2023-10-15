import cv2
import mediapipe as mp
import time

# Mediapipe 초기화
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# 화면 캡쳐 준비
cap = cv2.VideoCapture(0)

# 화면 크기
screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
screen_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# UI 색상
color_button_bg = (120, 120, 120)
color_button_text = (255, 255, 255)
color_menu_item_bg = (200, 200, 200)
color_menu_item_text = (0, 0, 0)
color_basket_bg = (0, 255, 0)
color_basket_text = (255, 255, 255)
color_selected_item_bg = (255, 0, 0)
color_selected_point = (0, 255, 0)

# 메뉴 항목 초기화
menu_items = [
    {'label': 'Menu 1', 'x1': 100, 'y1': 50, 'x2': 300, 'y2': 100},
    {'label': 'Menu 2', 'x1': 100, 'y1': 150, 'x2': 300, 'y2': 200},
    {'label': 'Menu 3', 'x1': 100, 'y1': 250, 'x2': 300, 'y2': 300}
]

# 장바구니 초기화
basket = []

# 메뉴 선택 결과
selected_menu = None
menu_selected = False

def draw_button(image, x1, y1, x2, y2, label, selected=False):
    # 버튼 영역 그리기
    if selected:
        cv2.rectangle(image, (x1, y1), (x2, y2), color_selected_item_bg, -1)
    else:
        cv2.rectangle(image, (x1, y1), (x2, y2), color_button_bg, -1)

    # 버튼 텍스트 그리기
    text_width, text_height = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][:2]
    text_x = int((x1 + x2 - text_width) / 2)
    text_y = int((y1 + y2 + text_height) / 2)
    text_color = color_button_text if not selected else color_selected_point
    cv2.putText(image, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)


def draw_menu_item(image, x1, y1, x2, y2, label, selected=False):
    # 메뉴 항목 영역 그리기
    if selected:
        cv2.rectangle(image, (x1, y1), (x2, y2), color_selected_item_bg, -1)
    else:
        cv2.rectangle(image, (x1, y1), (x2, y2), color_menu_item_bg, -1)

    # 메뉴 항목 텍스트 그리기
    text_width, text_height = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][:2]
    text_x = int((x1 + x2 - text_width) / 2)
    text_y = int((y1 + y2 + text_height) / 2)
    cv2.putText(image, label, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, color_menu_item_text, 2)


def draw_basket(image, x1, y1, x2, y2, items):
    # 장바구니 영역 그리기
    cv2.rectangle(image, (x1, y1), (x2, y2), color_basket_bg, -1)

    # 장바구니 아이템 그리기
    text_x = x1 + 10
    text_y = y1 + 30
    line_height = 30
    for item in items:
        cv2.putText(image, item, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_basket_text, 2)
        text_y += line_height


with mp_hands.Hands(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

    start_time = 0
    reset_button_x1, reset_button_y1 = 400, 50
    reset_button_x2, reset_button_y2 = 600, 100

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("카메라에서 프레임을 읽는 데 실패했습니다.")
            break

        # 좌우 반전
        image = cv2.flip(image, 1)

        # 이미지를 RGB로 변환하고 Mediapipe에 전달
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        # 메뉴 항목 그리기
        for item in menu_items:
            if selected_menu == item['label']:
                draw_menu_item(image, item['x1'], item['y1'], item['x2'], item['y2'], item['label'], selected=True)
            else:
                draw_menu_item(image, item['x1'], item['y1'], item['x2'], item['y2'], item['label'])

        # 장바구니 그리기
        draw_basket(image, 400, 100, 600, 500, basket)

        # Reset 버튼 그리기
        draw_button(image, reset_button_x1, reset_button_y1, reset_button_x2, reset_button_y2, "Reset")

        # 손가락 인식 및 그리기
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 검지손가락 끝 좌표 추출
                index_finger_landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                x, y = int(index_finger_landmark.x * screen_width), int(index_finger_landmark.y * screen_height)

                # 작은 점 그리기
                cv2.circle(image, (x, y), 5, (0, 255, 0), -1)

                # 메뉴 선택 확인
                for item in menu_items:
                    if item['x1'] < x < item['x2'] and item['y1'] < y < item['y2']:
                        selected_menu = item['label']
                        start_time = time.time()

                # Reset 버튼 선택 확인
                if reset_button_x1 < x < reset_button_x2 and reset_button_y1 < y < reset_button_y2:
                    if time.time() - start_time >= 2:
                        basket = []
                        selected_menu = None

        # 선택된 메뉴가 있을 경우
        if selected_menu:
            # 2초간 손 위치 정지 확인
            if time.time() - start_time >= 2:
                basket.append(selected_menu)
                selected_menu = None

        # 선택된 메뉴가 있을 경우 알림 표시
        if selected_menu:
            cv2.putText(image, f"Selected menu: {selected_menu}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)

        # 이미지 출력
        cv2.imshow('Menu Kiosk', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()