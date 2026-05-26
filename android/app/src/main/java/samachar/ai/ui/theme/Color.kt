package samachar.ai.ui.theme

import androidx.compose.ui.graphics.Color

object EditorialColors {
    // Light (warm paper)
    val LightBg        = Color(0xFFF4F1EA)
    val LightBgElev    = Color(0xFFFFFFFF)
    val LightBgSunk    = Color(0xFFECE7DC)
    val LightInk1      = Color(0xFF14171C)
    val LightInk2      = Color(0xFF4A5159)
    val LightInk3      = Color(0xFF8A8F96)
    val LightInk4      = Color(0xFFB6B2A6)
    val LightRule      = Color(0xFFE5E0D5)
    val LightRuleStrong = Color(0xFFC7C0B0)

    // Dark
    val DarkBg         = Color(0xFF14140F)
    val DarkBgElev     = Color(0xFF1B1B16)
    val DarkBgSunk     = Color(0xFF100F0B)
    val DarkInk1       = Color(0xFFF4F0E4)
    val DarkInk2       = Color(0xFFB4B0A4)
    val DarkInk3       = Color(0xFF7A766C)
    val DarkInk4       = Color(0xFF4D4A43)
    val DarkRule       = Color(0xFF2A2823)
    val DarkRuleStrong = Color(0xFF3A372F)

    // Semantic (shared)
    val AccentRed       = Color(0xFFC92A2A)   // live / breaking
    val AccentRedSoft   = Color(0xFFFAEFEE)
    val Verify          = Color(0xFF2D6A4F)
    val VerifySoft      = Color(0xFFECF3EE)
    val Info            = Color(0xFF1B3A5B)
    val InfoSoft        = Color(0xFFEAEFF5)
    val Warn            = Color(0xFF8A5A1C)
    val WarnSoft        = Color(0xFFF6EEDF)
}

// Convenience holder accessed from UI via SamacharTheme.palette
data class SamacharPalette(
    val bg: Color,
    val bgElev: Color,
    val bgSunk: Color,
    val ink1: Color,
    val ink2: Color,
    val ink3: Color,
    val ink4: Color,
    val rule: Color,
    val ruleStrong: Color,
    val accent: Color = EditorialColors.AccentRed,
    val accentSoft: Color = EditorialColors.AccentRedSoft,
    val verify: Color = EditorialColors.Verify,
    val verifySoft: Color = EditorialColors.VerifySoft,
    val info: Color = EditorialColors.Info,
    val infoSoft: Color = EditorialColors.InfoSoft,
    val warn: Color = EditorialColors.Warn,
    val warnSoft: Color = EditorialColors.WarnSoft,
)
