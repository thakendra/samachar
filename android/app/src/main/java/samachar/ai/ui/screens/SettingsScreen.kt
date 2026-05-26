package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowBack
import androidx.compose.material.icons.outlined.ChevronRight
import androidx.compose.material.icons.outlined.Language
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import samachar.ai.ui.components.*
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun SettingsScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val user by vm.user.collectAsState()
    var showWardDialog by remember { mutableStateOf(false) }
    var wardInput by remember { mutableStateOf(user?.ward ?: "") }
    if (user == null) return

    Column(Modifier.fillMaxSize()) {
        Row(Modifier.fillMaxWidth().padding(start = 8.dp, end = 20.dp, top = 8.dp, bottom = 8.dp),
            verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Outlined.ArrowBack, null, tint = palette.ink1,
                modifier = Modifier.padding(12.dp).size(16.dp).clickable { nav.popBackStack() })
            Text("Settings", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 18.sp, color = palette.ink1, modifier = Modifier.weight(1f))
            Spacer(Modifier.width(60.dp))
        }
        LazyColumn(Modifier.fillMaxSize()) {
            item {
                SectionHeader("APPEARANCE")
                Column(
                    Modifier.fillMaxWidth().padding(horizontal = 20.dp)
                        .clip(RoundedCornerShape(14.dp))
                        .background(palette.bgElev)
                        .border(1.dp, palette.rule, RoundedCornerShape(14.dp)),
                ) {
                    Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Text("Theme", fontSize = 13.5.sp, color = palette.ink1, modifier = Modifier.weight(1f))
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            listOf("light" to "Light", "dark" to "Dark").forEach { (v, l) ->
                                Pill(l, user!!.theme == v) { vm.updatePref("theme", v) }
                            }
                        }
                    }
                    Rule()
                    Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Text("Density", fontSize = 13.5.sp, color = palette.ink1, modifier = Modifier.weight(1f))
                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                            listOf("compact" to "Com", "comfortable" to "Std", "roomy" to "Roomy").forEach { (v, l) ->
                                Pill(l, user!!.density == v) { vm.updatePref("density", v) }
                            }
                        }
                    }
                    Rule()
                    Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically) {
                        Text("Accent", fontSize = 13.5.sp, color = palette.ink1, modifier = Modifier.weight(1f))
                        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                            listOf("#C92A2A", "#1B3A5B", "#2D6A4F", "#8A5A1C", "#5B4B8A").forEach { hex ->
                                val color = Color(android.graphics.Color.parseColor(hex))
                                Box(
                                    Modifier.size(22.dp).clip(RoundedCornerShape(6.dp))
                                        .background(color)
                                        .border(
                                            width = if (user!!.accent == hex) 2.dp else 0.dp,
                                            color = palette.ink1,
                                            shape = RoundedCornerShape(6.dp),
                                        )
                                        .clickable { vm.updatePref("accent", hex) }
                                )
                            }
                        }
                    }
                }
            }
            item {
                SectionHeader("LANGUAGE & LOCATION")
                Column(
                    Modifier.fillMaxWidth().padding(horizontal = 20.dp)
                        .clip(RoundedCornerShape(14.dp))
                        .background(palette.bgElev)
                        .border(1.dp, palette.rule, RoundedCornerShape(14.dp)),
                ) {
                    Row(
                        Modifier.fillMaxWidth().clickable {
                            vm.updatePref("language", if (user!!.language == "en") "np" else "en")
                        }.padding(horizontal = 16.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(Icons.Outlined.Language, null, tint = palette.ink2,
                            modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(12.dp))
                        Text("Headlines language", fontSize = 13.5.sp,
                            color = palette.ink1, modifier = Modifier.weight(1f))
                        MetaText(if (user!!.language == "np") "नेपाली" else "English")
                        Icon(Icons.Outlined.ChevronRight, null, tint = palette.ink3,
                            modifier = Modifier.padding(start = 8.dp).size(14.dp))
                    }
                    Rule()
                    Row(
                        Modifier.fillMaxWidth().clickable {
                            wardInput = user!!.ward; showWardDialog = true
                        }.padding(horizontal = 16.dp, vertical = 14.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(Icons.Outlined.LocationOn, null, tint = palette.ink2,
                            modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(12.dp))
                        Text("Your ward", fontSize = 13.5.sp,
                            color = palette.ink1, modifier = Modifier.weight(1f))
                        MetaText(user!!.ward)
                        Icon(Icons.Outlined.ChevronRight, null, tint = palette.ink3,
                            modifier = Modifier.padding(start = 8.dp).size(14.dp))
                    }
                }
            }
            item { Spacer(Modifier.height(40.dp)) }
        }
    }

    if (showWardDialog) {
        AlertDialog(
            onDismissRequest = { showWardDialog = false },
            confirmButton = {
                Button(onClick = {
                    vm.updatePref("ward", wardInput.trim())
                    showWardDialog = false
                }) { Text("Save") }
            },
            dismissButton = {
                TextButton(onClick = { showWardDialog = false }) { Text("Cancel") }
            },
            title = { Text("Set your ward") },
            text = {
                OutlinedTextField(wardInput, { wardInput = it }, singleLine = true,
                    modifier = Modifier.fillMaxWidth())
            }
        )
    }
}
