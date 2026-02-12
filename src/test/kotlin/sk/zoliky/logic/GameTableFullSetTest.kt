package sk.zoliky.logic

import org.junit.Assert.*
import org.junit.Test
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit

class GameTableFullSetTest {

    @Test
    fun `checkFullSets should automatically discard a set of 4 cards`() {
        val table = GameTable()
        table.startGame(listOf("P1", "P2"))
        val player = table.getCurrentPlayer()
        
        // Prepare a full set of Aces
        val aces = listOf(
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE),
            Card(Suit.SPADES, Rank.ACE)
        )
        
        // Give cards to player
        aces.forEach { player.hand.addCard(it) }
        
        // Bypass initial meld check
        player.hasMelded = true
        
        // Player melds the full set
        // Note: Initial meld requirement is 42 points. 4 Aces = 44 points (11*4). valid.
        table.meld(player.id, listOf(aces))
        
        // Assertions
        // The set should have been placed on table, THEN auto-discarded because it's full (4 cards).
        // So melds list should be empty (or the specific meld removed).
        
        assertTrue("Melds should be empty after auto-discard", table.melds.isEmpty())
        
        // Optional: Check if they went to discard pile?
        // Current implementation just removes them (vanish).
    }

    @Test
    fun `checkFullSets should NOT discard a set of 3 cards`() {
        val table = GameTable()
        table.startGame(listOf("P1", "P2"))
        val player = table.getCurrentPlayer()
        
        // Prepare a set of 3 Aces
        val aces = listOf(
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE)
        )
        // Give to player
        aces.forEach { player.hand.addCard(it) }
        
        player.hasMelded = true
        
        // Meld
        table.meld(player.id, listOf(aces))
        
        // Assertions
        assertEquals("Meld should remain on table", 1, table.melds.size)
        assertEquals("Meld should have 3 cards", 3, table.melds[0].size)
    }
    
    @Test
    fun `checkFullSets should discard when 4th card is added to existing set`() {
        val table = GameTable()
        table.startGame(listOf("P1", "P2"))
        val player = table.getCurrentPlayer()
        
        // 1. Meld 3 Aces
        val aces3 = listOf(
            Card(Suit.HEARTS, Rank.ACE),
            Card(Suit.DIAMONDS, Rank.ACE),
            Card(Suit.CLUBS, Rank.ACE)
        )
        aces3.forEach { player.hand.addCard(it) }
        
        player.hasMelded = true
        table.meld(player.id, listOf(aces3))
        
        assertEquals(1, table.melds.size)
        
        // 2. Add 4th Ace
        val aceSpades = Card(Suit.SPADES, Rank.ACE)
        player.hand.addCard(aceSpades)
        
        table.addToMeld(player.id, 0, aceSpades)
        
        // Assertions
        assertTrue("Melds should be empty after adding 4th card", table.melds.isEmpty())
    }
}
