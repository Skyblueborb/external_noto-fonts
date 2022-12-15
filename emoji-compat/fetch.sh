#!/usr/bin/env bash

set -o xtrace
set +e

METADATA_GIT="https://github.com/googlefonts/emojicompat.git"
FONT_GIT="https://github.com/googlefonts/noto-emoji.git"

SCRIPT_DIR=$(readlink -f $(dirname -- "$0"))
TMP_DIR=$(mktemp -d)

GIT_VERSION=$(git --version)
if [$? -ne 0]; then
   echo -e "ERROR: git not found"
   exit 1
fi

TTX_VERSION=$(ttx --version)

if [ $? -ne 0 ]; then
   echo "ERROR ttx required to check font"
   echo -e "\t python3 -m venv venv"
   echo -e "\t source venv/bin/activate"
   echo -e "\t pip install fonttools"
   exit 127
fi

echo "METADATA:    $METADATA_URL"
echo "FONT:        $FONT_URL"
echo "Updating in: $SCRIPT_DIR"

pushd $TMP_DIR > /dev/null

git clone --quiet --depth 1 --branch main $METADATA_GIT
METADATA_FILE="./emojicompat/src/emojicompat/emoji_metadata.txt"
# adjust newlines to avoid giant diffs
cat $METADATA_FILE | awk 'sub("$", "\r")' > emoji_metadata.txt

# pull the font
git clone --quiet --depth 1 --branch main $FONT_GIT
cp ./noto-emoji/fonts/NotoColorEmoji-emojicompat.ttf ./NewFont.ttf

ttx -o NewFont.ttx NewFont.ttf 2> /dev/null
grep -q 'header version="2.0"' NewFont.ttx

if [ $? -ne 0 ]; then
   echo -e "WRONG HEADER VERSION IN FONT FILE"
   echo -e "Expected 'header version=\"2.0\""
   echo -e "Found: "
   grep 'header version' NewFont.ttx
   exit 128
fi

cp emoji_metadata.txt $SCRIPT_DIR/data/emoji_metadata.txt
cp NewFont.ttf $SCRIPT_DIR/font/NotoColorEmojiCompat.ttf

popd > /dev/null
rm -rf $TMP_DIR
