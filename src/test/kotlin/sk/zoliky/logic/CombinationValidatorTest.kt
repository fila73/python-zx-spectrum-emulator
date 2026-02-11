package sk.zoliky.logic

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit

class CombinationValidatorTest {

    private val validator = CombinationValidator()

    // Helper to create cards
    private fun c(rank: Rank, suit: Suit) = Card(suit, rank)
    private fun joker() = Card(Suit.NONE, Rank.JOKER)

    @Test
    fun `isValidSet should return true for valid sets`() {
        // 3 cards, same rank, diff suits
        val set3 = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.SEVEN, Suit.DIAMONDS),
            c(Rank.SEVEN, Suit.CLUBS)
        )
        assertTrue(validator.isValidSet(set3))

        // 4 cards, same rank, diff suits
        val set4 = listOf(
            c(Rank.KING, Suit.HEARTS),
            c(Rank.KING, Suit.DIAMONDS),
            c(Rank.KING, Suit.CLUBS),
            c(Rank.KING, Suit.SPADES)
        )
        assertTrue(validator.isValidSet(set4)) // Assuming 4 suits exists
    }

    @Test
    fun `isValidSet should handle Jokers`() {
        // 7H, Joker, 7C
        val setWithJoker = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            joker(),
            c(Rank.SEVEN, Suit.CLUBS)
        )
        assertTrue(validator.isValidSet(setWithJoker))
        
        // 3 Jokers
        val allJokers = listOf(joker(), joker(), joker())
        assertTrue(validator.isValidSet(allJokers))
    }

    @Test
    fun `isValidSet should return false for invalid sets`() {
        // Rank mismatch
        val rankMismatch = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.EIGHT, Suit.DIAMONDS),
            c(Rank.SEVEN, Suit.CLUBS)
        )
        assertFalse(validator.isValidSet(rankMismatch))

        // Suit duplicate
        val suitDuplicate = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.SEVEN, Suit.CLUBS)
        )
        assertFalse(validator.isValidSet(suitDuplicate))

        // Too few cards
        val tooFew = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.SEVEN, Suit.DIAMONDS)
        )
        assertFalse(validator.isValidSet(tooFew))
    }

    @Test
    fun `isValidSequence should return true for valid sequences`() {
        // 7, 8, 9 of Hearts
        val seq3 = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.EIGHT, Suit.HEARTS),
            c(Rank.NINE, Suit.HEARTS)
        )
        assertTrue(validator.isValidSequence(seq3))

        // Low Ace: A, 2, 3
        val lowAce = listOf(
            c(Rank.ACE, Suit.CLUBS),
            c(Rank.TWO, Suit.CLUBS),
            c(Rank.THREE, Suit.CLUBS)
        )
        assertTrue(validator.isValidSequence(lowAce))

        // High Ace: Q, K, A
        val highAce = listOf(
            c(Rank.QUEEN, Suit.SPADES),
            c(Rank.KING, Suit.SPADES),
            c(Rank.ACE, Suit.SPADES)
        )
        assertTrue(validator.isValidSequence(highAce))
    }

    @Test
    fun `isValidSequence should handle Jokers`() {
        // 7, Joker, 9
        val jokerMid = listOf(
            c(Rank.SEVEN, Suit.DIAMONDS),
            joker(),
            c(Rank.NINE, Suit.DIAMONDS)
        )
        assertTrue(validator.isValidSequence(jokerMid))
        
        // Joker, 2, 3 (Ace represented by Joker?)
        val jokerEnd = listOf(
            joker(),
            c(Rank.TWO, Suit.CLUBS),
            c(Rank.THREE, Suit.CLUBS)
        )
        assertTrue(validator.isValidSequence(jokerEnd))
    }

    @Test
    fun `isValidSequence should return false for invalid sequences`() {
        // Suit mismatch
        val suitMismatch = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.EIGHT, Suit.DIAMONDS),
            c(Rank.NINE, Suit.HEARTS)
        )
        assertFalse(validator.isValidSequence(suitMismatch))

        // Gap too large
        val gap = listOf(
            c(Rank.SEVEN, Suit.HEARTS),
            c(Rank.NINE, Suit.HEARTS), // Missing 8
            c(Rank.TEN, Suit.HEARTS)
        )
        // Oops, 7, 9, 10 is missing 8. Wait, is it? 7->8->9->10.
        // It's a sequence of 3 cards: 7, 9, 10.
        // Gap between 7 and 9 is 1 (needs 1 joker).
        // Gap between 9 and 10 is 0.
        // If we have no jokers, it should fail.
        assertFalse(validator.isValidSequence(gap))
    }

    @Test
    fun `calculatePoints should return correct values`() {
        // Set of Aces: 10 + 10 + 10 = 30
        val aces = listOf(
            c(Rank.ACE, Suit.HEARTS),
            c(Rank.ACE, Suit.DIAMONDS),
            c(Rank.ACE, Suit.CLUBS)
        )
        assertEquals(30, validator.calculatePoints(aces))

        // Sequence Low Ace: A(1) + 2(2) + 3(3) = 6
        val lowAceSeq = listOf(
            c(Rank.ACE, Suit.CLUBS),
            c(Rank.TWO, Suit.CLUBS),
            c(Rank.THREE, Suit.CLUBS)
        )
        assertEquals(6, validator.calculatePoints(lowAceSeq))

        // Sequence High Ace: Q(10) + K(10) + A(11) = 31
        val highAceSeq = listOf(
            c(Rank.QUEEN, Suit.SPADES),
            c(Rank.KING, Suit.SPADES),
            c(Rank.ACE, Suit.SPADES)
        )
        assertEquals(31, validator.calculatePoints(highAceSeq))
        
        // Joker in sequence: 7(7) + Joker(8) + 9(9) = 24
        val jokerSeq = listOf(
            c(Rank.SEVEN, Suit.DIAMONDS),
            joker(),
            c(Rank.NINE, Suit.DIAMONDS)
        )
        assertEquals(24, validator.calculatePoints(jokerSeq))
    }
}
