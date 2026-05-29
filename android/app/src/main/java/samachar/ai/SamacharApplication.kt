package samachar.ai

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.util.Log
import com.google.firebase.FirebaseApp

class SamacharApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        // Firebase relies on Google Play Services. On emulators/devices with a
        // degraded or missing GMS, init can throw — never let that crash the app,
        // the news feed (Flask) works without Firebase.
        try {
            FirebaseApp.initializeApp(this)
        } catch (e: Throwable) {
            Log.e("SAM", "FirebaseApp.initializeApp failed: ${e.message}", e)
        }

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val channel = NotificationChannel(
                    "samachar_news",
                    "Samachar News Alerts",
                    NotificationManager.IMPORTANCE_DEFAULT,
                ).apply {
                    description = "Breaking news, AI briefs and ward alerts"
                }
                val nm = getSystemService(NotificationManager::class.java)
                nm?.createNotificationChannel(channel)
            }
        } catch (e: Throwable) {
            Log.e("SAM", "Notification channel setup failed: ${e.message}", e)
        }
    }
}
