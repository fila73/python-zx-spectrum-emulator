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
                PlayingCard(
                    resourceId = CardResources.getCardBackResource(),
                    onClick = { viewModel.drawCard() }
                )

                // Discard Pile
                if (state.discardPileTop != null) {
                    PlayingCard(
                        resourceId = CardResources.getCardResource(state.discardPileTop, androidx.compose.ui.platform.LocalContext.current),
                        onClick = { viewModel.drawFromDiscard() }
                    )
                } else {
                    // Empty slot placeholder
                    Box(
                        modifier = Modifier
                            .size(80.dp, 120.dp)
                            .background(Color.Black.copy(alpha = 0.2f))
                    ) {
                        Text("Empty", modifier = Modifier.align(Alignment.Center), color = Color.White)
                    }
                }
            }
            
            // Melds Area (Placeholder)
            Text("Melds on Table: ${state.meldsCount}")

            // Player Hand Area
            Text("Your Hand:")
            LazyRow(
                modifier = Modifier.fillMaxWidth().height(140.dp), // Increased height for selection offset / Zvětšená výška pro posun výběru
                horizontalArrangement = Arrangement.spacedBy((-30).dp), // Overlap cards / Překryv karet
                contentPadding = PaddingValues(horizontal = 16.dp)
            ) {
                val hand = state.currentPlayer?.hand?.getCards() ?: emptyList()
                items(count = hand.size) { index ->
                    val card = hand[index]
                    val isSelected = state.selectedCards.contains(index)
                    
                    Box(modifier = Modifier.padding(top = if (isSelected) 0.dp else 20.dp)) { // Selection offset / Posun při výběru
                         PlayingCard(
                            resourceId = CardResources.getCardResource(card, androidx.compose.ui.platform.LocalContext.current),
                            onClick = { viewModel.toggleCardSelection(index) }
                        )
                    }
                }
            }
            
            // Controls for selected cards
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                 Button(
                     onClick = { 
                         // Discard logic needs to be updated to handle specific card, for now just discard first selected
                         // Logika odhození potřebuje aktualizaci, zatím jen odhodíme první vybranou
                         state.selectedCards.firstOrNull()?.let { index -> viewModel.discardCard(index) }
                     },
                     enabled = state.selectedCards.isNotEmpty()
                 ) {
                     Text("Discard Selected")
                 }
            }
        }
    }
}

@Composable
fun PlayingCard(resourceId: Int, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .size(80.dp, 120.dp)
            .clickable(onClick = onClick),
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
        colors = CardDefaults.cardColors(containerColor = Color.Transparent) // Content is image / Obsah je obrázek
    ) {
        androidx.compose.foundation.Image(
            painter = androidx.compose.ui.res.painterResource(id = resourceId),
            contentDescription = null,
            modifier = Modifier.fillMaxSize(),
            contentScale = androidx.compose.ui.layout.ContentScale.Fit
        )
    }
}

