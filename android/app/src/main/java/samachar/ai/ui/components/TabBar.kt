package samachar.ai.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Explore
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.SamacharTheme

private data class Tab(val route: String, val label: String, val icon: ImageVector)

@Composable
fun TabBar(currentRoute: String, onClick: (String) -> Unit) {
    val palette = SamacharTheme.palette
    val tabs = listOf(
        Tab(Routes.HOME, "Today", Icons.Outlined.Home),
        Tab(Routes.DISCOVER, "Discover", Icons.Outlined.Explore),
        Tab(Routes.PREMIUM, "Pro", Icons.Outlined.AutoAwesome),
        Tab(Routes.PROFILE, "You", Icons.Outlined.Person),
    )
    Row(
        Modifier
            .fillMaxWidth()
            .background(palette.bgElev)
            .border(width = 1.dp, color = palette.rule)
            .padding(horizontal = 8.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceAround,
    ) {
        tabs.forEach { t ->
            val on = currentRoute == t.route
            Column(
                Modifier
                    .weight(1f)
                    .clickable { onClick(t.route) }
                    .padding(vertical = 6.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
            ) {
                Icon(
                    t.icon, null,
                    tint = if (on) palette.ink1 else palette.ink3,
                    modifier = Modifier.size(20.dp),
                )
                Spacer(Modifier.height(3.dp))
                Text(
                    t.label,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = if (on) palette.ink1 else palette.ink3,
                )
            }
        }
    }
}
