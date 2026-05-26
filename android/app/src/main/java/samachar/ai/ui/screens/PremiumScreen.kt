package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.*
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import samachar.ai.ui.components.*
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun PremiumScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()
    val user by vm.user.collectAsState()
    var billing by remember { mutableStateOf("monthly") }
    var busy by remember { mutableStateOf(false) }

    val price = if (billing == "monthly") "Rs 79" else "Rs 799"
    val per = if (billing == "monthly") "PER MONTH" else "PER YEAR (RS 66/MO)"

    fun toggle() {
        val u = user ?: return
        busy = true
        scope.launch {
            try {
                val newPlan = if (u.plan == "pro") "free" else "pro"
                val newQuota = if (newPlan == "pro") 999 else 10
                vm.auth.updateProfile(u.uid, mapOf("plan" to newPlan, "ai_quota" to newQuota))
                vm.refreshUser()
                vm.toast(if (newPlan == "pro") "Welcome to Pro!" else "Switched to Free")
            } catch (e: Exception) {
                vm.toast(e.message ?: "Subscribe failed")
            } finally { busy = false }
        }
    }

    LazyColumn(Modifier.fillMaxSize()) {
        item {
            Row(Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp),
                verticalAlignment = Alignment.CenterVertically) {
                Text("Premium", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                    fontSize = 22.sp, color = palette.ink1)
                Spacer(Modifier.weight(1f))
                MetaText(if (user?.plan == "pro") "ACTIVE" else "7-DAY TRIAL")
            }
        }
        // Hero
        item {
            Column(
                Modifier.fillMaxWidth().padding(start = 20.dp, end = 20.dp, top = 8.dp, bottom = 22.dp)
                    .border(width = 1.dp, color = palette.rule)
                    .padding(top = 8.dp, bottom = 22.dp),
            ) {
                Eyebrow("SAMACHAR PRO · FOR SERIOUS READERS")
                Spacer(Modifier.height(14.dp))
                Text(buildString { append("More signal."); append("\n"); append("Less of the rest.") },
                    fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
                    fontSize = 36.sp, color = palette.ink1, lineHeight = 40.sp)
                Spacer(Modifier.height(12.dp))
                Text("Unlimited AI chat, full bias-meter analysis, offline reading.",
                    fontSize = 14.sp, color = palette.ink2)
            }
        }
        // Features
        item { SectionHeader("WHAT'S INCLUDED", title = "Pro features") }
        item {
            Column(Modifier.padding(horizontal = 20.dp)) {
                listOf(
                    FeatureRow(Icons.Outlined.AutoAwesome, "Unlimited AI chat",
                        "Ask anything about any story, in any tone, with no daily ceiling."),
                    FeatureRow(Icons.Outlined.QueryStats, "Full bias meter",
                        "See how Nagarik, Ratopati and Setopati each frame the same story."),
                    FeatureRow(Icons.Outlined.Search, "Advanced search",
                        "Filter by district, publisher, date range, topic and sentiment."),
                    FeatureRow(Icons.Outlined.WifiOff, "Offline reading",
                        "Auto-save 200 articles. Built for travel and mountain districts."),
                ).forEachIndexed { i, f ->
                    FeatureItem(f, isFirst = i == 0)
                }
            }
        }
        // Billing toggle + card
        item { SectionHeader("UPGRADE · CHOOSE PLAN") }
        item {
            Column(Modifier.padding(horizontal = 20.dp)) {
                Row(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp))
                        .background(palette.bgSunk).padding(3.dp),
                    horizontalArrangement = Arrangement.spacedBy(3.dp),
                ) {
                    listOf("monthly" to "Monthly", "yearly" to "Yearly").forEach { (id, label) ->
                        Box(
                            Modifier.weight(1f).clip(RoundedCornerShape(9.dp))
                                .background(if (billing == id) palette.bgElev else androidx.compose.ui.graphics.Color.Transparent)
                                .clickable { billing = id }
                                .padding(vertical = 10.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(label, fontSize = 13.sp, fontWeight = FontWeight.SemiBold,
                                color = if (billing == id) palette.ink1 else palette.ink3)
                        }
                    }
                }
                Spacer(Modifier.height(14.dp))
                Column(
                    Modifier.fillMaxWidth().clip(RoundedCornerShape(14.dp))
                        .background(palette.bgElev)
                        .border(1.dp, palette.ink1, RoundedCornerShape(14.dp))
                        .padding(20.dp),
                ) {
                    Eyebrow("SAMACHAR PRO", color = palette.accent)
                    Spacer(Modifier.height(6.dp))
                    Text(price, fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                        fontSize = 38.sp, color = palette.ink1)
                    MetaText(per, modifier = Modifier.padding(top = 4.dp))
                    Spacer(Modifier.height(14.dp))
                    Rule()
                    Spacer(Modifier.height(8.dp))
                    listOf(
                        "Unlimited AI summaries & chat",
                        "Full bias meter",
                        "Advanced search",
                        "Offline reading",
                        "Ad-free experience",
                    ).forEach { f ->
                        Row(verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(vertical = 5.dp)) {
                            Icon(Icons.Outlined.Check, null, tint = palette.ink1,
                                modifier = Modifier.size(13.dp))
                            Spacer(Modifier.width(10.dp))
                            Text(f, fontSize = 13.sp, color = palette.ink1)
                        }
                    }
                    Spacer(Modifier.height(16.dp))
                    Button(
                        onClick = ::toggle, enabled = !busy,
                        modifier = Modifier.fillMaxWidth().height(46.dp),
                        shape = RoundedCornerShape(50),
                        colors = ButtonDefaults.buttonColors(containerColor = palette.ink1, contentColor = palette.bgElev),
                    ) {
                        Text(
                            if (user?.plan == "pro") "Downgrade to Free"
                            else "Start Pro · $price",
                            fontWeight = FontWeight.SemiBold, fontSize = 13.sp,
                        )
                    }
                    Spacer(Modifier.height(10.dp))
                    Text("7-DAY FREE TRIAL · CANCEL ANY TIME",
                        fontSize = 10.sp, color = palette.ink3,
                        modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center)
                }
                Spacer(Modifier.height(40.dp))
            }
        }
    }
}

private data class FeatureRow(val icon: ImageVector, val title: String, val desc: String)

@Composable
private fun FeatureItem(f: FeatureRow, isFirst: Boolean) {
    val palette = SamacharTheme.palette
    Column(Modifier.fillMaxWidth().border(width = 1.dp, color = palette.rule).padding(vertical = 16.dp)) {
        Row(verticalAlignment = Alignment.Top) {
            Box(
                Modifier.size(40.dp).clip(RoundedCornerShape(10.dp))
                    .background(palette.bgSunk),
                contentAlignment = Alignment.Center,
            ) {
                Icon(f.icon, null, tint = palette.ink1, modifier = Modifier.size(17.dp))
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(f.title, fontFamily = SerifFamily, fontSize = 17.sp,
                    fontWeight = FontWeight.SemiBold, color = palette.ink1)
                Spacer(Modifier.height(4.dp))
                Text(f.desc, fontSize = 12.5.sp, color = palette.ink2, lineHeight = 18.sp)
            }
        }
    }
}
