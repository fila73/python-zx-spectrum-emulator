package sk.zoliky.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import sk.zoliky.model.Card as ModelCard

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GameScreen(viewModel: GameViewModel = viewModel()) {
    val state = viewModel.uiState

    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Žolíky - ${state.currentPlayer?.name ?: "Loading"}") })
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Opponents Area (Placeholder)
            Text("Opponents: ${state.players.size - 1}")

            // Game Table Area
            Row(
                modifier = Modifier.fillMaxWidth().height(200.dp).background(Color(0xFF2E7D32)), // Green felt color
                horizontalArrangement = Arrangement.SpaceEvenly,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Deck
                CardPlaceholder(text = "Deck\n(${state.deckCount})") {
                    viewModel.drawCard()
                }

                // Discard Pile
                val discardText = if (state.discardPileTop != null) 
                    "${state.discardPileTop?.rank}\n${state.discardPileTop?.suit}" 
                else "Empty"
                
                CardPlaceholder(text = "Discard\n$discardText") {
                    viewModel.drawFromDiscard()
                }
            }
            
            // Melds Area (Placeholder)
            Text("Melds on Table: ${state.meldsCount}")

            // Player Hand Area
            Text("Your Hand:")
            LazyRow(
                modifier = Modifier.fillMaxWidth().height(120.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val hand = state.currentPlayer?.hand?.getCards() ?: emptyList()
                items(count = hand.size) { index ->
                    val card = hand[index]
                    PlayingCard(card = card) {
                        viewModel.discardCard(index)
                    }
                }
            }
        }
    }
}

@Composable
fun CardPlaceholder(text: String, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .size(80.dp, 120.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = Color.White)
    ) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text(text, color = Color.Black)
        }
    }
}

@Composable
fun PlayingCard(card: ModelCard, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .size(80.dp, 120.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text(
                text = "${card.rank}\n${card.suit}",
                color = if (card.suit.name == "HEARTS" || card.suit.name == "DIAMONDS") Color.Red else Color.Black
            )
        }
    }
}
