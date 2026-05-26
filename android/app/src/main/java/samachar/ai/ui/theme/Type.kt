package samachar.ai.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// System serifs/sans — replace with bundled Google Fonts later if desired.
val SerifFamily = FontFamily.Serif
val SansFamily = FontFamily.SansSerif
val MonoFamily = FontFamily.Monospace

val SamacharTypography = Typography(
    displayLarge = TextStyle(
        fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 34.sp, lineHeight = 38.sp, letterSpacing = (-0.5).sp
    ),
    displayMedium = TextStyle(
        fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 28.sp, lineHeight = 32.sp, letterSpacing = (-0.4).sp
    ),
    headlineLarge = TextStyle(
        fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp, lineHeight = 26.sp
    ),
    titleMedium = TextStyle(
        fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
        fontSize = 17.sp, lineHeight = 21.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = SansFamily, fontWeight = FontWeight.Normal,
        fontSize = 14.sp, lineHeight = 22.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = SansFamily, fontWeight = FontWeight.Normal,
        fontSize = 13.sp, lineHeight = 20.sp
    ),
    labelSmall = TextStyle(
        fontFamily = MonoFamily, fontWeight = FontWeight.Medium,
        fontSize = 11.sp, lineHeight = 14.sp, letterSpacing = 1.5.sp
    ),
)
