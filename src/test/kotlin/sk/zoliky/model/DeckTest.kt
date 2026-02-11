package sk.zoliky.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class DeckTest {

    @Test
    fun `deck should have 108 cards on initialization`() {
        val deck = Deck()
        assertEquals(108, deck.size())
    }

    @Test
    fun `deck should contain 4 jokers`() {
        val deck = Deck()
        val cards = deck.deal(108)
        val jokers = cards.filter { it.rank == Rank.JOKER }
        assertEquals(4, jokers.size)
    }

    @Test
    fun `deck should deal correct number of cards`() {
        val deck = Deck()
        val dealt = deck.deal(10)
        assertEquals(10, dealt.size)
        assertEquals(98, deck.size())
    }

    @Test
    fun `shuffle should change card order`() {
        val deck1 = Deck()
        val deck2 = Deck()
        
        // Save initial state logic check
        // Probability of shuffling to same order is extremely low
        deck1.shuffle()
        
        val cards1 = deck1.deal(108)
        val cards2 = deck2.deal(108)
        
        assertNotEquals(cards1, cards2)
    }
    
    @Test(expected = IllegalArgumentException::class)
    fun `deal should throw exception if not enough cards`() {
        val deck = Deck()
        deck.deal(109)
    }
}
