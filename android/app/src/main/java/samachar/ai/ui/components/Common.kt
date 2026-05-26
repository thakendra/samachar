package samachar.ai.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material.icons.filled.Circle
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import samachar.ai.ui.theme.MonoFamily
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily

@Composable
fun Eyebrow(text: String, color: Color = SamacharTheme.palette.ink3, modifier: Modifier = Modifier) {
    Text(
        text = text.uppercase(),
        modifier = modifier,
        color = color,
        fontSize = 10.5.sp,
        fontFamily = MonoFamily,
        fontWeight = FontWeight.Medium,
        letterSpacing = 1.6.sp,
    )
}

@Composable
fun MetaText(text: String, modifier: Modifier = Modifier, color: Color = SamacharTheme.palette.ink3) {
    Text(
        text = text, modifier = modifier, color = color,
        fontSize = 11.sp, fontFamily = MonoFamily,
        letterSpacing = 0.4.sp,
    )
}

@Composable
fun Rule(modifier: Modifier = Modifier) {
    Box(
        modifier
            .fillMaxWidth()
            .height(1.dp)
            .background(SamacharTheme.palette.rule)
    )
}

@Composable
fun Tag(
    text: String,
    bg: Color = SamacharTheme.palette.bgSunk,
    fg: Color = SamacharTheme.palette.ink2,
    modifier: Modifier = Modifier,
) {
    Box(
        modifier
            .clip(RoundedCornerShape(4.dp))
            .background(bg)
            .padding(horizontal = 7.dp, vertical = 3.dp)
    ) {
        Text(
            text = text.uppercase(),
            color = fg,
            fontSize = 10.sp,
            fontFamily = MonoFamily,
            fontWeight = FontWeight.Medium,
            letterSpacing = 1.0.sp,
        )
    }
}

@Composable
fun Dot(color: Color = SamacharTheme.palette.accent, size: Int = 6) {
    Box(
        Modifier
            .size(size.dp)
            .clip(CircleShape)
            .background(color)
    )
}

@Composable
fun IconButton34(icon: ImageVector, onClick: () -> Unit, color: Color = SamacharTheme.palette.ink1, badge: Boolean = false) {
    Box(
        modifier = Modifier
            .size(38.dp)
            .clip(CircleShape)
            .background(SamacharTheme.palette.bgElev)
            .border(1.dp, SamacharTheme.palette.rule, CircleShape)
            .clickable(onClick = onClick),
        contentAlignment = Alignment.Center,
    ) {
        Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(16.dp))
        if (badge) {
            Box(
                Modifier
                    .align(Alignment.TopEnd)
                    .padding(8.dp)
                    .size(7.dp)
                    .clip(CircleShape)
                    .background(SamacharTheme.palette.accent)
                    .border(2.dp, SamacharTheme.palette.bgElev, CircleShape)
            )
        }
    }
}

@Composable
fun SectionHeader(eyebrow: String, title: String? = null, action: String? = null, onAction: (() -> Unit)? = null) {
    Row(
        Modifier
            .fillMaxWidth()
            .padding(start = 20.dp, end = 20.dp, top = 24.dp, bottom = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Column(Modifier.weight(1f)) {
            Eyebrow(eyebrow)
            if (title != null) {
                Text(
                    title,
                    fontFamily = SerifFamily,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 20.sp,
                    color = SamacharTheme.palette.ink1,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
        }
        if (action != null) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .clip(RoundedCornerShape(6.dp))
                    .clickable { onAction?.invoke() }
                    .padding(4.dp)
            ) {
                Text(
                    action,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = SamacharTheme.palette.ink1,
                )
                Icon(Icons.Outlined.ArrowForward, null,
                    tint = SamacharTheme.palette.ink1,
                    modifier = Modifier
                        .padding(start = 4.dp)
                        .size(14.dp))
            }
        }
    }
}

@Composable
fun Pill(text: String, on: Boolean, onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(50))
            .background(if (on) palette.ink1 else Color.Transparent)
            .border(
                width = 1.dp,
                color = if (on) palette.ink1 else palette.rule,
                shape = RoundedCornerShape(50),
            )
            .clickable(onClick = onClick)
            .padding(horizontal = 13.dp, vertical = 7.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text,
            color = if (on) palette.bgElev else palette.ink2,
            fontSize = 12.5.sp,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Composable
fun BiasMeter(position: Int, big: Boolean = false) {
    val palette = SamacharTheme.palette
    Box(
        Modifier
            .fillMaxWidth()
            .height(if (big) 6.dp else 4.dp)
            .clip(RoundedCornerShape(2.dp))
            .background(palette.bgSunk),
    ) {
        // Pin
        Box(
            Modifier
                .fillMaxWidth(position / 100f)
                .padding(end = 1.dp)
                .height((if (big) 14 else 10).dp)
                .background(Color.Transparent),
        )
        Box(
            Modifier
                .offset(x = ((position / 100f) * 300).dp - 1.dp, y = (if (big) -4 else -3).dp)
                .size(width = 2.dp, height = (if (big) 14 else 10).dp)
                .background(palette.ink1)
        )
    }
}

@Composable
fun Toast(message: String?) {
    AnimatedVisibility(visible = message != null) {
        Box(
            Modifier
                .fillMaxWidth()
                .padding(bottom = 100.dp),
            contentAlignment = Alignment.BottomCenter,
        ) {
            if (message != null) {
                Box(
                    Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(SamacharTheme.palette.ink1)
                        .padding(horizontal = 18.dp, vertical = 12.dp)
                ) {
                    Text(
                        message,
                        color = SamacharTheme.palette.bgElev,
                        fontSize = 13.sp,
                        fontWeight = FontWeight.SemiBold,
                        textAlign = TextAlign.Center,
                    )
                }
            }
        }
    }
}
