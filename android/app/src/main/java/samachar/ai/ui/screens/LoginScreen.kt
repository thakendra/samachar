package samachar.ai.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.ArrowForward
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
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
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import kotlinx.coroutines.launch
import samachar.ai.ui.components.Eyebrow
import samachar.ai.ui.components.MetaText
import samachar.ai.ui.components.Rule
import samachar.ai.ui.theme.SamacharTheme
import samachar.ai.ui.theme.SerifFamily
import samachar.ai.viewmodel.AppViewModel

@Composable
fun LoginScreen(vm: AppViewModel, nav: NavController) {
    val palette = SamacharTheme.palette
    val scope = rememberCoroutineScope()

    var mode by remember { mutableStateOf("login") } // login | signup
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var ward by remember { mutableStateOf("Ward 5, Lalitpur") }
    var busy by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    val isSignup = mode == "signup"

    fun submit() {
        if (busy) return
        if (email.isBlank() || password.length < 6) {
            error = "Email and password (6+ chars) required"; return
        }
        if (isSignup && name.isBlank()) {
            error = "Your name is required to sign up"; return
        }
        busy = true; error = null
        scope.launch {
            try {
                val profile = if (isSignup) vm.auth.signUp(email.trim(), password, name.trim(), ward.trim())
                else vm.auth.signIn(email.trim(), password)
                vm.setUser(profile)
            } catch (e: Exception) {
                error = e.message ?: "Authentication failed"
            } finally {
                busy = false
            }
        }
    }

    fun anon() {
        if (busy) return
        // In login mode there is no name field, so never block the guest flow on
        // a missing name — fall back to a sensible default.
        val guestName = name.trim().ifBlank { "Guest" }
        busy = true; error = null
        scope.launch {
            try {
                val profile = vm.auth.signInAnonymous(guestName, ward.trim())
                vm.setUser(profile)
            } catch (e: Exception) {
                error = e.message ?: "Sign-in failed"
            } finally { busy = false }
        }
    }

    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(28.dp)
    ) {
        Spacer(Modifier.height(20.dp))
        Row(verticalAlignment = Alignment.Bottom) {
            Text("samachar", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 30.sp, color = palette.ink1)
            Text(".", fontFamily = SerifFamily, fontWeight = FontWeight.Bold,
                fontSize = 30.sp, color = palette.accent)
        }
        MetaText("NEPAL'S NEWS, UNDERSTOOD", color = palette.ink3)

        Spacer(Modifier.height(30.dp))
        Text(if (isSignup) "Create your account" else "Welcome back",
            fontFamily = SerifFamily, fontWeight = FontWeight.SemiBold,
            fontSize = 28.sp, color = palette.ink1)
        Spacer(Modifier.height(12.dp))
        Text(
            if (isSignup)
                "Sign up to save bookmarks, post comments and chat with the AI editor."
            else "Sign in to your samachar account.",
            fontSize = 14.sp, color = palette.ink2,
        )

        Spacer(Modifier.height(24.dp))

        if (isSignup) {
            Eyebrow("YOUR NAME"); Spacer(Modifier.height(6.dp))
            OutlinedTextField(name, { name = it }, singleLine = true,
                modifier = Modifier.fillMaxWidth(),
                placeholder = { Text("e.g. Ramesh Thapa") })
            Spacer(Modifier.height(14.dp))
        }

        Eyebrow("EMAIL"); Spacer(Modifier.height(6.dp))
        OutlinedTextField(email, { email = it.trim() }, singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("you@example.com") })

        Spacer(Modifier.height(14.dp))
        Eyebrow("PASSWORD"); Spacer(Modifier.height(6.dp))
        OutlinedTextField(password, { password = it }, singleLine = true,
            visualTransformation = PasswordVisualTransformation(),
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text("•••••• (6+ chars)") })

        if (isSignup) {
            Spacer(Modifier.height(14.dp))
            Eyebrow("YOUR WARD"); Spacer(Modifier.height(6.dp))
            OutlinedTextField(ward, { ward = it }, singleLine = true,
                modifier = Modifier.fillMaxWidth())
        }

        if (error != null) {
            Spacer(Modifier.height(14.dp))
            Box(
                Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    .background(palette.accentSoft)
                    .padding(10.dp)
            ) {
                Text(error!!, color = palette.accent, fontSize = 12.5.sp)
            }
        }

        Spacer(Modifier.height(22.dp))
        Button(
            onClick = ::submit,
            enabled = !busy,
            modifier = Modifier.fillMaxWidth().height(48.dp),
            shape = RoundedCornerShape(50),
            colors = ButtonDefaults.buttonColors(containerColor = palette.ink1, contentColor = palette.bgElev),
        ) {
            if (busy) CircularProgressIndicator(color = palette.bgElev, strokeWidth = 2.dp,
                modifier = Modifier.size(18.dp))
            else {
                Text(if (isSignup) "Create account" else "Sign in",
                    fontWeight = FontWeight.SemiBold, fontSize = 13.sp)
                Spacer(Modifier.width(6.dp))
                Icon(Icons.Outlined.ArrowForward, null, modifier = Modifier.size(16.dp))
            }
        }

        Spacer(Modifier.height(10.dp))
        TextButton(onClick = { mode = if (isSignup) "login" else "signup"; error = null },
            modifier = Modifier.align(Alignment.CenterHorizontally)) {
            Text(if (isSignup) "Already have an account? Sign in"
                 else "New to samachar? Create an account",
                fontSize = 12.sp, color = palette.ink3)
        }

        Spacer(Modifier.height(24.dp))
        Rule()
        Spacer(Modifier.height(16.dp))
        Eyebrow("OR — QUICK START")
        Spacer(Modifier.height(8.dp))
        TextButton(onClick = ::anon, modifier = Modifier.fillMaxWidth()) {
            Text("Continue as guest (anonymous)",
                fontSize = 13.sp, color = palette.ink1, fontWeight = FontWeight.Medium)
        }
    }
}
