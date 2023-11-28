# Copyright (C) 2013 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# We have to use PRODUCT_PACKAGES (together with BUILD_PREBUILT) instead of
# PRODUCT_COPY_FILES to install the font files, so that the NOTICE file can
# get installed too.

PRODUCT_PACKAGES := \
    NotoColorEmoji.ttf \
    NotoNaskhArabic-Bold.ttf \
    NotoNaskhArabic-Regular.ttf \
    NotoNaskhArabicUI-Bold.ttf \
    NotoNaskhArabicUI-Regular.ttf \
    NotoSansAdlam-VF.ttf \
    NotoSansAhom-Regular.otf \
    NotoSansAnatolianHieroglyphs-Regular.otf \
    NotoSansArmenian-Bold.ttf \
    NotoSansArmenian-Regular.ttf \
    NotoSansAvestan-Regular.ttf \
    NotoSansBalinese-Regular.ttf \
    NotoSansBamum-Regular.ttf \
    NotoSansBassaVah-Regular.otf \
    NotoSansBatak-Regular.ttf \
    NotoSansBengali-Bold.ttf \
    NotoSansBengali-Regular.ttf \
    NotoSansBengaliUI-Bold.ttf \
    NotoSansBengaliUI-Regular.ttf \
    NotoSansBhaiksuki-Regular.otf \
    NotoSansBrahmi-Regular.ttf \
    NotoSansBuginese-Regular.ttf \
    NotoSansBuhid-Regular.ttf \
    NotoSansCanadianAboriginal-Regular.ttf \
    NotoSansCarian-Regular.ttf \
    NotoSansChakma-Regular.ttf \
    NotoSansCham-Bold.ttf \
    NotoSansCham-Regular.ttf \
    NotoSansCherokee-Regular.ttf \
    NotoSansCJK-Regular.ttc \
    NotoSansCoptic-Regular.ttf \
    NotoSansCuneiform-Regular.ttf \
    NotoSansCypriot-Regular.ttf \
    NotoSansDeseret-Regular.ttf \
    NotoSansDevanagari-Bold.ttf \
    NotoSansDevanagari-Regular.ttf \
    NotoSansDevanagariUI-Bold.ttf \
    NotoSansDevanagariUI-Regular.ttf \
    NotoSansEgyptianHieroglyphs-Regular.ttf \
    NotoSansElbasan-Regular.otf \
    NotoSansEthiopic-Bold.ttf \
    NotoSansEthiopic-Regular.ttf \
<<<<<<< HEAD   (586902 Merge "Snap for 5754798 from 35600966a2ba2a3b8c1b311066113db)
    NotoSansGeorgian-Bold.ttf \
    NotoSansGeorgian-Regular.ttf \
=======
    NotoSansGeorgian-VF.ttf \
>>>>>>> BRANCH (8f6cec Merge "Revert "Revert "Bump emojicompat bundled font to 15"")
    NotoSansGlagolitic-Regular.ttf \
    NotoSansGothic-Regular.ttf \
    NotoSansGujarati-Bold.ttf \
    NotoSansGujarati-Regular.ttf \
    NotoSansGujaratiUI-Bold.ttf \
    NotoSansGujaratiUI-Regular.ttf \
    NotoSansGunjalaGondi-Regular.otf \
    NotoSansGurmukhi-Bold.ttf \
    NotoSansGurmukhi-Regular.ttf \
    NotoSansGurmukhiUI-Bold.ttf \
    NotoSansGurmukhiUI-Regular.ttf \
    NotoSansHanifiRohingya-Regular.otf \
    NotoSansHanunoo-Regular.ttf \
    NotoSansHatran-Regular.otf \
    NotoSansHebrew-Bold.ttf \
    NotoSansHebrew-Regular.ttf \
    NotoSansImperialAramaic-Regular.ttf \
    NotoSansInscriptionalPahlavi-Regular.ttf \
    NotoSansInscriptionalParthian-Regular.ttf \
    NotoSansJavanese-Regular.otf \
    NotoSansKaithi-Regular.ttf \
    NotoSansKannada-Bold.ttf \
    NotoSansKannada-Regular.ttf \
    NotoSansKannadaUI-Bold.ttf \
    NotoSansKannadaUI-Regular.ttf \
    NotoSansKayahLi-Regular.ttf \
    NotoSansKharoshthi-Regular.ttf \
    NotoSansKhmer-VF.ttf \
    NotoSansKhmerUI-Bold.ttf \
    NotoSansKhmerUI-Regular.ttf \
    NotoSansKhojki-Regular.otf \
    NotoSansLao-Bold.ttf \
    NotoSansLao-Regular.ttf \
    NotoSansLaoUI-Bold.ttf \
    NotoSansLaoUI-Regular.ttf \
    NotoSansLepcha-Regular.ttf \
    NotoSansLimbu-Regular.ttf \
    NotoSansLinearA-Regular.otf \
    NotoSansLinearB-Regular.ttf \
    NotoSansLisu-Regular.ttf \
    NotoSansLycian-Regular.ttf \
    NotoSansLydian-Regular.ttf \
    NotoSansMalayalam-Bold.ttf \
    NotoSansMalayalam-Regular.ttf \
    NotoSansMalayalamUI-Bold.ttf \
    NotoSansMalayalamUI-Regular.ttf \
    NotoSansMandaic-Regular.ttf \
    NotoSansManichaean-Regular.otf \
    NotoSansMarchen-Regular.otf \
    NotoSansMasaramGondi-Regular.otf \
    NotoSansMeeteiMayek-Regular.ttf \
    NotoSansMeroitic-Regular.otf \
    NotoSansMiao-Regular.otf \
    NotoSansMongolian-Regular.ttf \
    NotoSansMro-Regular.otf \
    NotoSansMultani-Regular.otf \
    NotoSansMyanmar-Bold.ttf \
    NotoSansMyanmar-Regular.ttf \
    NotoSansMyanmarUI-Bold.ttf \
    NotoSansMyanmarUI-Regular.ttf \
    NotoSansNabataean-Regular.otf \
    NotoSansNewa-Regular.otf \
    NotoSansNewTaiLue-Regular.ttf \
    NotoSansNKo-Regular.ttf \
    NotoSansOgham-Regular.ttf \
    NotoSansOlChiki-Regular.ttf \
    NotoSansOldItalic-Regular.ttf \
    NotoSansOldNorthArabian-Regular.otf \
    NotoSansOldPermic-Regular.otf \
    NotoSansOldPersian-Regular.ttf \
    NotoSansOldSouthArabian-Regular.ttf \
    NotoSansOldTurkic-Regular.ttf \
    NotoSansOriya-Bold.ttf \
    NotoSansOriya-Regular.ttf \
    NotoSansOriyaUI-Bold.ttf \
    NotoSansOriyaUI-Regular.ttf \
    NotoSansOsage-Regular.ttf \
    NotoSansOsmanya-Regular.ttf \
    NotoSansPahawhHmong-Regular.otf \
    NotoSansPalmyrene-Regular.otf \
    NotoSansPauCinHau-Regular.otf \
    NotoSansPhagsPa-Regular.ttf \
    NotoSansPhoenician-Regular.ttf \
    NotoSansRejang-Regular.ttf \
    NotoSansRunic-Regular.ttf \
    NotoSansSamaritan-Regular.ttf \
    NotoSansSaurashtra-Regular.ttf \
    NotoSansSharada-Regular.otf \
    NotoSansShavian-Regular.ttf \
    NotoSansSinhala-Bold.ttf \
    NotoSansSinhala-Regular.ttf \
    NotoSansSinhalaUI-Bold.otf \
    NotoSansSinhalaUI-Regular.otf \
    NotoSansSoraSompeng-Regular.otf \
    NotoSansSundanese-Regular.ttf \
    NotoSansSylotiNagri-Regular.ttf \
    NotoSansSymbols-Regular-Subsetted.ttf \
    NotoSansSymbols-Regular-Subsetted2.ttf \
    NotoSansSyriacEastern-Regular.ttf \
    NotoSansSyriacEstrangela-Regular.ttf \
    NotoSansSyriacWestern-Regular.ttf \
    NotoSansTagalog-Regular.ttf \
    NotoSansTagbanwa-Regular.ttf \
    NotoSansTaiLe-Regular.ttf \
    NotoSansTaiTham-Regular.ttf \
    NotoSansTaiViet-Regular.ttf \
    NotoSansTamil-Bold.ttf \
    NotoSansTamil-Regular.ttf \
    NotoSansTamilUI-Bold.ttf \
    NotoSansTamilUI-Regular.ttf \
    NotoSansTelugu-Bold.ttf \
    NotoSansTelugu-Regular.ttf \
    NotoSansTeluguUI-Bold.ttf \
    NotoSansTeluguUI-Regular.ttf \
    NotoSansThaana-Bold.ttf \
    NotoSansThaana-Regular.ttf \
    NotoSansThai-Bold.ttf \
    NotoSansThai-Regular.ttf \
    NotoSansThaiUI-Bold.ttf \
    NotoSansThaiUI-Regular.ttf \
    NotoSansTibetan-Bold.ttf \
    NotoSansTibetan-Regular.ttf \
    NotoSansTifinagh-Regular.otf \
    NotoSansUgaritic-Regular.ttf \
    NotoSansVai-Regular.ttf \
    NotoSansWancho-Regular.otf \
    NotoSansWarangCiti-Regular.otf \
    NotoSansYi-Regular.ttf \
    NotoSerif-Bold.ttf \
    NotoSerif-BoldItalic.ttf \
    NotoSerif-Italic.ttf \
    NotoSerif-Regular.ttf \
    NotoSerifArmenian-Bold.ttf \
    NotoSerifArmenian-Regular.ttf \
    NotoSerifBengali-Bold.ttf \
    NotoSerifBengali-Regular.ttf \
    NotoSerifCJK-Regular.ttc \
    NotoSerifDevanagari-Bold.ttf \
    NotoSerifDevanagari-Regular.ttf \
    NotoSerifEthiopic-Bold.otf \
    NotoSerifEthiopic-Regular.otf \
<<<<<<< HEAD   (586902 Merge "Snap for 5754798 from 35600966a2ba2a3b8c1b311066113db)
    NotoSerifGeorgian-Bold.ttf \
    NotoSerifGeorgian-Regular.ttf \
=======
    NotoSerifGeorgian-VF.ttf \
>>>>>>> BRANCH (8f6cec Merge "Revert "Revert "Bump emojicompat bundled font to 15"")
    NotoSerifGujarati-Bold.ttf \
    NotoSerifGujarati-Regular.ttf \
    NotoSerifGurmukhi-Bold.otf \
    NotoSerifGurmukhi-Regular.otf \
    NotoSerifHebrew-Bold.ttf \
    NotoSerifHebrew-Regular.ttf \
    NotoSerifKannada-Bold.ttf \
    NotoSerifKannada-Regular.ttf \
    NotoSerifKhmer-Bold.otf \
    NotoSerifKhmer-Regular.otf \
    NotoSerifLao-Bold.ttf \
    NotoSerifLao-Regular.ttf \
    NotoSerifMalayalam-Bold.ttf \
    NotoSerifMalayalam-Regular.ttf \
    NotoSerifMyanmar-Bold.otf \
    NotoSerifMyanmar-Regular.otf \
    NotoSerifSinhala-Bold.otf \
    NotoSerifSinhala-Regular.otf \
    NotoSerifTamil-Bold.ttf \
    NotoSerifTamil-Regular.ttf \
    NotoSerifTelugu-Bold.ttf \
    NotoSerifTelugu-Regular.ttf \
    NotoSerifThai-Bold.ttf \
    NotoSerifThai-Regular.ttf
