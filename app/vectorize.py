import cv2
import ezdxf
import svgwrite

def image_to_vector(image_path, dxf_path, svg_path):
    img = cv2.imread(image_path)
    h, w, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(
        thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # DXF setup
    dxf_doc = ezdxf.new()
    dxf_msp = dxf_doc.modelspace()

    # SVG setup
    dwg = svgwrite.Drawing(svg_path, size=(w, h))

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        if len(approx) >= 3:
            pts = [(int(p[0][0]), int(p[0][1])) for p in approx]

            # DXF (invert Y-axis)
            dxf_pts = [(x, -y) for x, y in pts]
            dxf_msp.add_lwpolyline(dxf_pts, close=True)

            # SVG
            dwg.add(
                dwg.polygon(
                    points=pts,
                    fill="none",
                    stroke="black",
                    stroke_width=2
                )
            )

    # Circle detection
    circles = cv2.HoughCircles(
        gray, cv2.HOUGH_GRADIENT, 1.2, 50,
        param1=50, param2=30,
        minRadius=10, maxRadius=300
    )

    if circles is not None:
        for c in circles[0]:
            x, y, r = c

            dxf_msp.add_circle((int(x), -int(y)), int(r))
            dwg.add(
                dwg.circle(
                    center=(int(x), int(y)),
                    r=int(r),
                    fill="none",
                    stroke="red",
                    stroke_width=2
                )
            )

    dxf_doc.saveas(dxf_path)
    dwg.save()
