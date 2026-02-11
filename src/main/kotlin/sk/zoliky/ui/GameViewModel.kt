package sk.zoliky.ui

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import sk.zoliky.logic.GameTable
import sk.zoliky.logic.Player

class GameViewModel : ViewModel() {
    private val gameTable = GameTable()
    
    // Simple state exposure for MVP
    // In real app, use StateFlow/LiveData
    var uiState by mutableStateOf(GameUiState())
        private set

    init {
        // Start game with 2 players for testing
        gameTable.startGame(listOf("Player 1", "Opponent"))
        updateState()
    }

    fun drawCard() {
        try {
            val currentPlayer = gameTable.getCurrentPlayer()
            gameTable.drawCard(currentPlayer.id)
            updateState()
        } catch (e: Exception) {
            // Handle error (e.g. show Snackbar)
            println("Error drawing card: ${e.message}")
        }
    }

    fun drawFromDiscard() {
        try {
            val currentPlayer = gameTable.getCurrentPlayer()
            gameTable.drawFromDiscard(currentPlayer.id)
            updateState()
        } catch (e: Exception) {
            println("Error drawing from discard: ${e.message}")
        }
    }

    fun discardCard(cardIndex: Int) {
        try {
            val currentPlayer = gameTable.getCurrentPlayer()
            val card = currentPlayer.hand.getCards()[cardIndex]
            gameTable.discardCard(currentPlayer.id, card)
            updateState()
        } catch (e: Exception) {
             println("Error discarding card: ${e.message}")
        }
    }

    private fun updateState() {
        uiState = GameUiState(
            currentPlayer = gameTable.getCurrentPlayer(),
            players = gameTable.players,
            discardPileTop = gameTable.discardPile.lastOrNull(),
            deckCount = gameTable.deck.size(),
            meldsCount = gameTable.melds.size
        )
    }
}

data class GameUiState(
    val currentPlayer: Player? = null,
    val players: List<Player> = emptyList(),
    val discardPileTop: sk.zoliky.model.Card? = null,
    val deckCount: Int = 0,
    val meldsCount: Int = 0
)
