package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.NotificationsActive
import androidx.compose.material.icons.outlined.QueryStats
import androidx.compose.material.icons.outlined.Star
import androidx.compose.material.icons.outlined.ThumbUp
import androidx.compose.material.icons.outlined.Warning
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import samachar.ai.data.model.Notification
import samachar.ai.ui.components.Dot
import samachar.ai.ui.components.MetaText
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun NotificationsScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val user by vm.user.collectAsState()
    val notifs by vm.allNotifs.collectAsState()
    val read by vm.readNotifs.collectAsState()

    LaunchedEffect(user?.uid) { vm.refreshNotifications() }

    fun markRead(n: Notification) {
        val uid = user?.uid ?: return
        if (n.id in read) return
        scope.launch {
            vm.notifications.markRead(uid, n.id)
            vm.refreshNotifications()
        }
    }
    fun markAll() {
        val uid = user?.uid ?: return
        scope.launch {
            vm.notifications.markAllRead(uid)
            vm.refreshNotifications()
        }
    }

    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(start = 8.dp, end = 20.dp, top = 8.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.ArrowBack, null, tint = palette.ink1,
                modifier = Modifier.padding(12.dp).size(16.dp).clickable { nav.popBackStack() })
            Text("Notifications", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 18.sp, color = palette.ink1, modifier = Modifier.weight(1f))
            Text("Mark read", color = palette.ink3, fontSize = 12.sp,
                modifier = Modifier.clickable { markAll() })
        }
        LazyColumn(Modifier.fillMaxSize().padding(horizontal = 20.dp)) {
            items(notifs) { n -> NotifRow(n, isRead = n.id in read) { markRead(n) } }
        }
    }
}

@Composable
private fun NotifRow(n: Notification, isRead: Boolean, onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    val color = when (n.tone) {
        "live" -> palette.accent
        "info" -> palette.info
        "verify" -> palette.verify
        "warn" -> palette.warn
        else -> palette.ink2
    }
    val icon: ImageVector = when (n.icon) {
        "alert" -> Icons.Outlined.Warning
        "sparkle" -> Icons.Outlined.AutoAwesome
        "thumb-up" -> Icons.Outlined.ThumbUp
        "star" -> Icons.Outlined.Star
        "chart" -> Icons.Outlined.QueryStats
        else -> Icons.Outlined.NotificationsActive
    }
    Row(
        Modifier.fillMaxWidth().clickable(onClick = onClick)
            .border(width = 1.dp, color = palette.rule)
            .padding(vertical = 16.dp),
        verticalAlignment = Alignment.Top,
    ) {
        Box(
            Modifier.size(36.dp).clip(CircleShape).background(palette.bgElev)
                .border(1.dp, color, CircleShape),
            contentAlignment = Alignment.Center,
        ) {
            Icon(icon, null, tint = color, modifier = Modifier.size(15.dp))
        }
        Spacer(Modifier.width(14.dp))
        Column(Modifier.weight(1f)) {
            Text(n.title, fontFamily = SerifFamily, fontSize = 14.sp,
                fontWeight = FontWeight.SemiBold,
                color = if (isRead) palette.ink2 else palette.ink1)
            Spacer(Modifier.height(4.dp))
            MetaText(n.sub)
        }
        if (!isRead) Dot(color = color)
    }
}
