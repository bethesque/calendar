from rendering import *
from google_calendar import CalendarDay, Event

weekdays = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
LEFT_WIDTH = 75


def layout_calendars(calendars: list[CalendarDay], surface):
    image = Image.new(
        "RGB", (surface.right, surface.bottom), surface.BLACK
    )  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    box = EqualChildrenBox(padding=5, stroke=0)
    h1_font = font(size=FONT_SIZE_H1)
    

    for day in calendars:
        day_box = StackChildrenBox(padding=5, stroke=0, horizontal=False)
        day_box.children.append(
            Text(
                f"{weekdays[day.date.weekday()]} {day.date.strftime('%d/%m/%Y')}",
                font=h1_font,
                color=WHITE,
            ),
        )

        for event in day.whole_day_events:
            summary = extract_summary(event)
            summary_font = decide_summary_font(event)

            day_box.children.append(
                RightStretchBox(
                    fill=WHITE,
                    margin=2,
                    left_width=LEFT_WIDTH,
                    left=Text(event.owner),
                    right=Text(summary, font=summary_font, color=BLACK),
                )
            )
        for event in day.timed_events:
            summary = extract_summary(event)
            summary_font = decide_summary_font(event)

            day_box.children.append(
                RightStretchBox(
                    fill=WHITE,
                    margin=2,
                    left_width=LEFT_WIDTH,
                    left=Text(
                        f"{event.owner}\n{event.start_time.strftime('%I:%M %p')}"
                    ),
                    right=Text(summary, font=summary_font, padding_top=4, color=BLACK),
                )
            )

        box.children.append(day_box)

    # spacing = 20
    # for i in range(int(480 / spacing)):
    #     t = i * spacing - 1
    #     b = i * spacing
    #     r = (380, t, 390, b)
    #     draw.rectangle(r, RED)

    box.render(draw, surface)

    # draw.text((5, 0), 'hello beth', font = font, fill = surface.RED)

    # draw.line((5, 170, 80, 245), fill = surface.RED)
    # draw.line((80, 170, 5, 245), fill = surface.YELLOW)
    # draw.rectangle((5, 170, 80, 245), outline = surface.BLACK)
    # draw.rectangle((90, 170, 165, 245), fill = surface.YELLOW)
    # draw.arc((5, 250, 80, 325), 0, 360, fill = surface.BLACK)
    # draw.chord((90, 250, 165, 325), 0, 360, fill = surface.RED)
    return image


def extract_summary(event):
    return "*** " + event.summary.upper() + " ***" if event.description and "#veryimportant" in event.description else event.summary

def decide_summary_font(event):
    important = (event.description and "#important" in event.description) or (event.description and "#veryimportant" in event.description) or (not event.recurring and (event.description is None or not "#notimportant" in event.description))
    return important_font(size=FONT_SIZE_SUMMARY) if important else font(size=FONT_SIZE_SUMMARY)
