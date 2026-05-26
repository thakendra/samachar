package samachar.ai.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.Whatshot
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import samachar.ai.ui.theme.MonoFamily
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily

@Composable
fun TopBar(
    ward: String,
    streakDays: Int = 24,
    unread: Int,
    onNotifClick: () -> Unit,
    onProfileClick: () -> Unit,
) {
    val palette = SamacharTheme.palette
    Column(Modifier.fillMaxWidth().padding(top = 8.dp)) {
        Row(
            Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Row(verticalAlignment = Alignment.Bottom) {
                Text(
                    "samachar",
                    fontFamily = SerifFamily,
                    fontWeight = FontWeight.Bold,
                    fontSize = 22.sp,
                    color = palette.ink1,
                )
                Text(
                    ".",
                    fontFamily = SerifFamily,
                    fontWeight = FontWeight.Bold,
                    fontSize = 22.sp,
                    color = palette.accent,
                )
                Spacer(Modifier.width(6.dp))
                Text(
                    "AI · NP",
                    fontFamily = MonoFamily,
                    fontSize = 9.5.sp,
                    letterSpacing = 1.7.sp,
                    color = palette.ink3,
                    modifier = Modifier.padding(bottom = 4.dp),
                )
            }
            Spacer(Modifier.weight(1f))
            IconButton34(Icons.Outlined.Notifications, onNotifClick, badge = unread > 0)
            Spacer(Modifier.width(8.dp))
            IconButton34(Icons.Outlined.Person, onProfileClick)
        }

        Row(
            Modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Outlined.LocationOn, null, tint = palette.ink3,
                modifier = Modifier.size(13.dp))
            Spacer(Modifier.width(10.dp))
            MetaText(ward, color = palette.ink2)
            Spacer(Modifier.width(10.dp))
            Box(
                Modifier
                    .weight(1f)
                    .height(1.dp)
                    .background(palette.rule)
            )
            Spacer(Modifier.width(10.dp))
            Icon(Icons.Outlined.Whatshot, null, tint = palette.accent,
                modifier = Modifier.size(13.dp))
            Spacer(Modifier.width(5.dp))
            MetaText("$streakDays DAY", color = palette.ink1)
        }
    }
}
