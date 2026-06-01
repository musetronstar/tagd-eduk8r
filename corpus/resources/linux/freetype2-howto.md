# Adding Fonts

Linux Uses the Freetype 2 font system. If you would like to add a font to your system, it will become available in GIMP and many other applications.

1. Go to your favorite font website and download a font package. In this example, I downloaded "Fira Code" to my `~/Downloads` directory.

2. Open a terminal:

```bash
# in your home directory
cd ~

# make a personal fonts directory
mkdir .fonts
cd .fonts

# unpack your font files into this directory (mine is `fira-code.zip` - use the filename you downloaded)
unzip ~/Downloads/fira-code.zip

# update the font cache so the change can be seen by the system
fc-cache
```

3. Open GIMP or other application that uses the Freetype 2 font system and select the font you added.
