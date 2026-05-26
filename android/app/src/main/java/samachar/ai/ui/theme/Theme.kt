package samachar.ai.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.staticCompositionLocalOf

val LocalPalette = staticCompositionLocalOf {
    SamacharPalette(
        bg = EditorialColors.LightBg,
        bgElev = EditorialColors.LightBgElev,
        bgSunk = EditorialColors.LightBgSunk,
        ink1 = EditorialColors.LightInk1,
        ink2 = EditorialColors.LightInk2,
        ink3 = EditorialColors.LightInk3,
        ink4 = EditorialColors.LightInk4,
        rule = EditorialColors.LightRule,
        ruleStrong = EditorialColors.LightRuleStrong,
    )
}

private val lightPalette = SamacharPalette(
    bg = EditorialColors.LightBg,
    bgElev = EditorialColors.LightBgElev,
    bgSunk = EditorialColors.LightBgSunk,
    ink1 = EditorialColors.LightInk1,
    ink2 = EditorialColors.LightInk2,
    ink3 = EditorialColors.LightInk3,
    ink4 = EditorialColors.LightInk4,
    rule = EditorialColors.LightRule,
    ruleStrong = EditorialColors.LightRuleStrong,
)

private val darkPalette = SamacharPalette(
    bg = EditorialColors.DarkBg,
    bgElev = EditorialColors.DarkBgElev,
    bgSunk = EditorialColors.DarkBgSunk,
    ink1 = EditorialColors.DarkInk1,
    ink2 = EditorialColors.DarkInk2,
    ink3 = EditorialColors.DarkInk3,
    ink4 = EditorialColors.DarkInk4,
    rule = EditorialColors.DarkRule,
    ruleStrong = EditorialColors.DarkRuleStrong,
)

@Composable
fun SamacharTheme(
    dark: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val palette = if (dark) darkPalette else lightPalette
    val colorScheme = if (dark)
        darkColorScheme(
            primary = palette.ink1, onPrimary = palette.bg,
            background = palette.bg, onBackground = palette.ink1,
            surface = palette.bgElev, onSurface = palette.ink1,
            error = palette.accent,
        )
    else
        lightColorScheme(
            primary = palette.ink1, onPrimary = palette.bg,
            background = palette.bg, onBackground = palette.ink1,
            surface = palette.bgElev, onSurface = palette.ink1,
            error = palette.accent,
        )

    CompositionLocalProvider(LocalPalette provides palette) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = SamacharTypography,
            content = content,
        )
    }
}

object SamacharTheme {
    val palette: SamacharPalette
        @Composable get() = LocalPalette.current
}
