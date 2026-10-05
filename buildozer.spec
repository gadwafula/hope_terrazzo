[app]

# Title of your application
title = Hope Terrazzo

# Package name (no spaces or special chars)
package.name = hopeterrazzo

# Package domain (needed for Android package ID)
package.domain = org.hopeterrazzo

# Source code location
source.dir = .

# Source files to include
source.include_exts = py,png,jpg,kv,atlas

# Application versioning
version = 1.0.0

# Application requirements
requirements = python3,kivy

# Supported orientations
orientation = portrait

# Fullscreen behavior
fullscreen = 0

# Android specific configurations
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]

# Log level (2 = verbose debug output)
log_level = 2

# Display warning if buildozer is run as root
warn_on_root = 1
