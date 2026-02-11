package sk.zoliky

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import sk.zoliky.ui.GameScreen
import sk.zoliky.ui.theme.ZolikyTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ZolikyTheme {
                GameScreen()
            }
        }
    }
}
