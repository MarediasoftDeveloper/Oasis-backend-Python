# views.py

from django.http import JsonResponse


ANDROID_PACKAGE_NAME = "com.myoasis.app"

ANDROID_SHA256_FINGERPRINT = (
   "ED:37:C5:2B:1A:ab:71:02:"
   "24:C5:B1:99:37:2E:45:D0:"
   "F2:DC:D5:47:C0:95:CD:2A:"
   "07:8A:3F:D8:3B:BE:10:B0"
)

APPLE_TEAM_ID = "HTUZ7FUW9R"

APPLE_BUNDLE_ID = "com.myoasis.oasis"

def assetlinks(request):
    return JsonResponse(
        [
            {
                "relation": [
                    "delegate_permission/common.handle_all_urls"
                ],
                "target": {
                    "namespace": "android_app",
                    "package_name": ANDROID_PACKAGE_NAME,
                    "sha256_cert_fingerprints": [
                        ANDROID_SHA256_FINGERPRINT
                    ],
                },
            }
        ],
        safe=False,
    )


def apple_app_site_association(request):
    app_id = f"{APPLE_TEAM_ID}.{APPLE_BUNDLE_ID}"

    return JsonResponse(
        {
            "applinks": {
                "details": [
                    {
                        "appIDs": [
                            app_id
                        ],
                        "components": [
                            {
                                "/": "/oasis/api/scan/trails/*",
                                "comment": "Venue MyOasis trail QR links",
                            },
                            {
                                "/": "/oasis/api/scan/challenges/*",
                                "comment": "Venue MyOasis challenge QR links",
                            },
                        ],
                    }
                ]
            }
        }
    )