{
  "targets": [
    {
      "target_name": "ai_game_dev_native",
      "sources": [
        "src/native/ai_game_dev.cc",
        "src/native/game_generator.cc",
        "src/native/utils.cc"
      ],
      "include_dirs": [
        "<!(node -e \"require('nan')\")",
        "../../core/ai-game-dev/include",
        "../../go/lib"
      ],
      "libraries": [
        "-L../../go/lib",
        "-lai_game_dev"
      ],
      "cflags": [
        "-std=c++17",
        "-fPIC"
      ],
      "cflags_cc": [
        "-std=c++17", 
        "-fPIC"
      ],
      "conditions": [
        ['OS=="mac"', {
          "xcode_settings": {
            "OTHER_CPLUSPLUSFLAGS": ["-std=c++17", "-stdlib=libc++"],
            "OTHER_LDFLAGS": ["-stdlib=libc++"],
            "MACOSX_DEPLOYMENT_TARGET": "10.7"
          }
        }],
        ['OS=="win"', {
          "msvs_settings": {
            "VCCLCompilerTool": {
              "AdditionalOptions": ["/std:c++17"]
            }
          }
        }]
      ]
    }
  ]
}