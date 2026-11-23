import nh3
import markdown
import time
import os

from django.shortcuts import render
from google import genai
from google.genai import types, errors

from .models import RoomImage


def home(request):
    print("HOME VIEW CALLED", request.method, flush=True)

    if request.method == "POST":
        image = request.FILES.get("room_image")

        if not image:
            return render(request, "rooms/home.html", {
                "error": "Please upload an image."
            })

        if not image.content_type.startswith("image/"):
            return render(request, "rooms/home.html", {
                "error": "Please upload a valid image."
            })

        if image.size > 10 * 1024 * 1024:
            return render(request, "rooms/home.html", {
                "error": "Image must be smaller than 10 MB."
            })

        room = RoomImage.objects.create(image=image)

        try:
            client = genai.Client(
                api_key=os.environ["GEMINI_API_KEY"]
            )

            with room.image.open("rb") as file:
                image_bytes = file.read()

            prompt = """
Analyze this uploaded room photo as a professional interior designer.

Provide the following sections:

1. ROOM STYLE DETECTION
Identify the interior design style and explain why.

2. COLORS AND FURNITURE
Identify the main colors, furniture, and decorations visible.

3. FURNITURE RECOMMENDATIONS
Suggest 5 suitable furniture or decoration items.
Explain why each item matches the room.

4. COLOR PALETTE
Recommend 4 matching colors for the room.
Explain where each color should be used.

5. LIGHTING SUGGESTIONS
Suggest suitable lighting improvements.

6. BUDGET-FRIENDLY MAKEOVER
Suggest improvements within a total budget of Rs. 10000.
Give approximate prices in Indian Rupees.
Make sure the total stays within the budget.

7. SPACE OPTIMIZATION
Suggest 3 ways to make the room more organized and spacious.

Use simple English.
Use clear headings and numbered lists.
Do not assume objects are present if they are not visible.
Prices are estimates, not verified store prices.
"""

            # Retry Gemini API up to 3 times
            for attempt in range(3):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.5-flash-lite",
                        contents=[
                            types.Part.from_bytes(
                                data=image_bytes,
                                mime_type=image.content_type
                            ),
                            prompt
                        ]
                    )
                    break

                except errors.ServerError as e:
                    if e.code not in (500, 502, 503, 504):
                        raise

                    if attempt == 2:
                        raise

                    print("Gemini server busy. Retrying...")
                    time.sleep(2 ** (attempt + 1))

            # Save AI analysis to database
            analysis = response.text or "No analysis returned."
            room.analysis = analysis
            room.save()

            return render(request, "rooms/home.html", {
                "uploaded_image": room.image.url,
                "success": True,
                "analysis": analysis
            })

        except Exception as e:
            print("GEMINI ERROR:", str(e), flush=True)

            return render(request, "rooms/home.html", {
                "uploaded_image": room.image.url,
                "error": "AI analysis failed. Check your API key, quota and terminal logs."
            })

    return render(request, "rooms/home.html")



def analysis_history(request):
    rooms = RoomImage.objects.exclude(
        analysis=""
    ).order_by("-uploaded_at")

    for room in rooms:
        html = markdown.markdown(
            room.analysis,
            extensions=["extra", "sane_lists"]
        )

        room.formatted_analysis = nh3.clean(html)

    return render(request, "rooms/history.html", {
        "rooms": rooms
    })
