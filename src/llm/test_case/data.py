UV_loc_string1="""Now you get the positions for passenger requests and taxi vehicles, respectively. Every position is represented as [longitude, latitude].
The passenger requests are as follows:
{
    "78942": {
        "origin": [
            104.0412682,
            30.6669185
        ],
        "destination": [
            104.1438647,
            30.6276377
        ]
    },
    "81088": {
        "origin": [
            104.0562247,
            30.6223237
        ],
        "destination": [
            104.0738543,
            30.6970738
        ]
    }
}	,where `key` is the `request id`, and `value` represents its ideal pickup position and drop-off position.
The taxi vehicles are as follows:
{
    "17": [
        104.0581489,
        30.6792291
    ],
    "12": [
        104.0566995,
        30.6722262
    ]
}	,where `key` is the `taxi id`, and `value` represents the current position of the vehicle.
Please use the appropriate tools to assign each request to a single taxi reasonably."""
