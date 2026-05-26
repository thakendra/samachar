package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import samachar.ai.ui.components.*
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun ProfileScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val user by vm.user.collectAsState()
    val bookmarkIds by vm.bookmarkIds.collectAsState()
    val unread by vm.unreadNotifs.collectAsState()
    if (user == null) return

    val initials = user!!.name.split(" ").mapNotNull { it.firstOrNull() }.take(2)
        .joinToString("").uppercase().ifBlank { "YO" }

    LazyColumn(Modifier.fillMaxSize()) {
        item {
            Row(
                Modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("You", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                    fontSize = 22.sp, color = palette.ink1)
                Spacer(Modifier.weight(1f))
                IconButton34(Icons.Outlined.Settings, { nav.navigate(Routes.SETTINGS) })
            }
        }

        // Identity card
        item {
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    Modifier.size(56.dp).clip(CircleShape).background(palette.ink1),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(initials, fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                        fontSize = 20.sp, color = palette.bgElev)
                }
                Spacer(Modifier.width(14.dp))
                Column(Modifier.weight(1f)) {
                    Text(user!!.name, fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
                        fontSize = 18.sp, color = palette.ink1)
                    Spacer(Modifier.height(2.dp))
                    MetaText(user!!.ward.uppercase())
                }
            }
        }

        // Stats row
        item {
            Row(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)
                    .clip(RoundedCornerShape(14.dp))
                    .background(palette.bgElev)
                    .border(1.dp, palette.rule, RoundedCornerShape(14.dp))
                    .padding(horizontal = 20.dp, vertical = 18.dp),
            ) {
                StatCell("${bookmarkIds.size}", "SAVED") { nav.navigate(Routes.BOOKMARKS) }
                StatCell("24", "DAY STREAK")
                StatCell("$unread", "UNREAD") { nav.navigate(Routes.NOTIFICATIONS) }
            }
        }

        // Plan section
        item {
            SectionHeader(
                eyebrow = "YOUR PLAN",
                title = if (user!!.plan == "pro") "Reader · Pro" else "Reader · Free",
                action = "Compare",
                onAction = { nav.navigate(Routes.PREMIUM) },
            )
            Column(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)
                    .clip(RoundedCornerShape(14.dp))
                    .background(palette.bgElev)
                    .border(1.dp, palette.rule, RoundedCornerShape(14.dp))
                    .padding(18.dp),
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Eyebrow("AI USAGE · TODAY")
                    Spacer(Modifier.weight(1f))
                    Text(if (user!!.plan == "pro") "∞" else "${user!!.aiQuota} / 10",
                        fontFamily = androidx.compose.ui.text.font.FontFamily.Monospace,
                        fontSize = 12.sp, fontWeight = FontWeight.Bold, color = palette.ink1)
                }
                Spacer(Modifier.height(8.dp))
                Box(
                    Modifier.fillMaxWidth().height(4.dp).clip(RoundedCornerShape(2.dp))
                        .background(palette.bgSunk),
                ) {
                    val fraction = if (user!!.plan == "pro") 1f
                        else user!!.aiQuota.coerceIn(0, 10) / 10f
                    Box(Modifier.fillMaxHeight().fillMaxWidth(fraction).background(palette.ink1))
                }
                if (user!!.plan != "pro") {
                    Spacer(Modifier.height(14.dp))
                    Row(
                        Modifier.fillMaxWidth().clip(RoundedCornerShape(10.dp))
                            .border(1.dp, palette.ink1, RoundedCornerShape(10.dp))
                            .clickable { nav.navigate(Routes.PREMIUM) }
                            .padding(horizontal = 14.dp, vertical = 12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(Icons.Outlined.AutoAwesome, null, tint = palette.ink1,
                            modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(10.dp))
                        Column(Modifier.weight(1f)) {
                            Text("Try Pro · 7 days free", fontFamily = SerifFamily,
                                fontSize = 14.sp, fontWeight = FontWeight.SemiBold, color = palette.ink1)
                            MetaText("RS 79/MO · CANCEL ANY TIME")
                        }
                        Icon(Icons.Outlined.ArrowForward, null, tint = palette.ink1,
                            modifier = Modifier.size(14.dp))
                    }
                }
            }
        }

        // Library
        item {
            SectionHeader("LIBRARY")
            Column(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)
                    .clip(RoundedCornerShape(14.dp))
                    .background(palette.bgElev)
                    .border(1.dp, palette.rule, RoundedCornerShape(14.dp)),
            ) {
                LibraryRow(Icons.Outlined.Bookmark, "Saved articles", "${bookmarkIds.size}") { nav.navigate(Routes.BOOKMARKS) }
                Rule()
                LibraryRow(Icons.Outlined.AutoAwesome, "AI conversations", "") { nav.navigate(Routes.AI) }
                Rule()
                LibraryRow(Icons.Outlined.Notifications, "Notifications", "$unread unread") { nav.navigate(Routes.NOTIFICATIONS) }
                Rule()
                LibraryRow(Icons.Outlined.Settings, "Settings", "") { nav.navigate(Routes.SETTINGS) }
            }
        }

        // Sign out
        item {
            Box(
                Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 24.dp),
                contentAlignment = Alignment.Center,
            ) {
                TextButton(onClick = { vm.signOut() }) {
                    Icon(Icons.Outlined.Logout, null, tint = palette.accent,
                        modifier = Modifier.size(14.dp))
                    Spacer(Modifier.width(6.dp))
                    Text("Sign out", color = palette.accent, fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}

@Composable
private fun RowScope.StatCell(n: String, label: String, onClick: (() -> Unit)? = null) {
    val palette = SamacharTheme.palette
    Column(Modifier.weight(1f).then(
        if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier
    )) {
        Text(n, fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
            fontSize = 28.sp, color = palette.ink1)
        MetaText(label)
    }
}

@Composable
private fun LibraryRow(icon: ImageVector, label: String, value: String, onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    Row(
        Modifier.fillMaxWidth().clickable(onClick = onClick).padding(horizontal = 16.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Icon(icon, null, tint = palette.ink2, modifier = Modifier.size(16.dp))
        Spacer(Modifier.width(14.dp))
        Text(label, fontSize = 13.5.sp, color = palette.ink1, modifier = Modifier.weight(1f))
        if (value.isNotBlank()) MetaText(value, color = palette.ink2)
        Spacer(Modifier.width(8.dp))
        Icon(Icons.Outlined.ChevronRight, null, tint = palette.ink3, modifier = Modifier.size(14.dp))
    }
}
