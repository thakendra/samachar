package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowOutward
import androidx.compose.material.icons.outlined.AutoAwesome
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Send
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import samachar.ai.data.model.Trend
import samachar.ai.ui.components.*
import samachar.ai.ui.navigation.Routes
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

private val SUGGESTED = listOf(
    "Why is gold price rising in Nepal?",
    "Summarise the federal budget for farmers",
    "How will Pulchowk roadworks affect my commute?",
    "NEPSE: which sectors lead the rally?",
    "Explain Nepal's federal structure in one minute",
)

@Composable
fun DiscoverScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    var q by remember { mutableStateOf("") }
    var trends by remember { mutableStateOf<List<Trend>>(emptyList()) }

    LaunchedEffect(Unit) {
        try { trends = vm.notifications.trends() } catch (_: Exception) {}
    }

    fun askAi(query: String) {
        if (query.isBlank()) return
        vm.setPendingAi(query.trim())
        nav.navigate(Routes.AI)
    }

    fun doSearch(query: String) {
        vm.setSearchQuery(query.trim())
        nav.navigate(Routes.SEARCH)
    }

    Column(Modifier.fillMaxSize()) {
        Row(
            Modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text("Discover", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 22.sp, color = palette.ink1)
            Spacer(Modifier.weight(1f))
            IconButton34(Icons.Outlined.Settings, { nav.navigate(Routes.SETTINGS) })
        }

        // AI ask bar
        Row(
            Modifier.fillMaxWidth().padding(horizontal = 20.dp)
                .clip(RoundedCornerShape(14.dp))
                .background(palette.ink1)
                .padding(horizontal = 14.dp, vertical = 4.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Outlined.AutoAwesome, null, tint = palette.bgElev, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(10.dp))
            OutlinedTextField(
                value = q, onValueChange = { q = it },
                placeholder = { Text("Ask AI anything about Nepal…", color = palette.bgElev.copy(alpha = 0.5f), fontSize = 13.5.sp) },
                singleLine = true,
                colors = OutlinedTextFieldDefaults.colors(
                    focusedTextColor = palette.bgElev, unfocusedTextColor = palette.bgElev,
                    cursorColor = palette.bgElev,
                    focusedBorderColor = Color.Transparent, unfocusedBorderColor = Color.Transparent,
                    focusedContainerColor = Color.Transparent, unfocusedContainerColor = Color.Transparent,
                ),
                modifier = Modifier.weight(1f),
            )
            Icon(Icons.Outlined.Send, null, tint = palette.bgElev,
                modifier = Modifier.size(16.dp).clickable { askAi(q) })
        }

        Spacer(Modifier.height(12.dp))

        // Search shortcut
        Row(
            Modifier.fillMaxWidth().padding(horizontal = 20.dp)
                .clip(RoundedCornerShape(14.dp))
                .background(palette.bgElev)
                .border(1.dp, palette.rule, RoundedCornerShape(14.dp))
                .clickable { doSearch(q) }
                .padding(horizontal = 14.dp, vertical = 12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Icon(Icons.Outlined.Search, null, tint = palette.ink3, modifier = Modifier.size(16.dp))
            Spacer(Modifier.width(10.dp))
            Text("Search the archive", color = palette.ink3, fontSize = 13.sp, modifier = Modifier.weight(1f))
        }

        LazyColumn(Modifier.fillMaxSize()) {
            item { SectionHeader("TRENDING NOW · NEPAL") }
            items(trends) { t -> TrendRow(t) { doSearch(t.title) } }
            item { SectionHeader("ASK AI · POPULAR") }
            items(SUGGESTED) { s -> SuggestionRow(s) { askAi(s) } }
            item { Spacer(Modifier.height(40.dp)) }
        }
    }
}

@Composable
private fun TrendRow(t: Trend, onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    val color = when (t.heat) {
        "hot" -> palette.accent; "breaking" -> palette.warn
        "rising" -> palette.verify; "new" -> palette.info
        else -> palette.ink3
    }
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 20.dp).clickable(onClick = onClick)
            .border(width = 1.dp, color = palette.rule)
            .padding(vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("%02d".format(t.rank), fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
            fontSize = 26.sp, color = palette.ink1, modifier = Modifier.padding(end = 14.dp))
        Column(Modifier.weight(1f)) {
            Text(t.title, fontFamily = SerifFamily, fontSize = 15.sp,
                fontWeight = FontWeight.SemiBold, color = palette.ink1)
            MetaText(t.sub)
        }
        Box(
            Modifier.clip(RoundedCornerShape(4.dp))
                .border(1.dp, color, RoundedCornerShape(4.dp))
                .padding(horizontal = 7.dp, vertical = 3.dp)
        ) {
            Text(t.heat.uppercase(), fontSize = 10.sp, color = color,
                fontWeight = FontWeight.Medium, letterSpacing = 1.0.sp)
        }
    }
}

@Composable
private fun SuggestionRow(text: String, onClick: () -> Unit) {
    val palette = SamacharTheme.palette
    Row(
        Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 4.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(palette.bgElev)
            .border(1.dp, palette.rule, RoundedCornerShape(12.dp))
            .clickable(onClick = onClick)
            .padding(horizontal = 14.dp, vertical = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(text, fontFamily = SerifFamily, fontSize = 14.sp,
            color = palette.ink1, modifier = Modifier.weight(1f))
        Icon(Icons.Outlined.ArrowOutward, null, tint = palette.ink3,
            modifier = Modifier.size(14.dp))
    }
}
