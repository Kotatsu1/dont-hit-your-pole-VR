import xr

# Query the available VR/AR extensions
available = xr.enumerate_instance_extension_properties()

# Replace with whatever extensions are required for your
# particular application...
required = [xr.KHR_OPENGL_ENABLE_EXTENSION_NAME, ]
for prop in required:
    assert prop in available


"https://github.com/cmbruns/pyopenxr_examples"