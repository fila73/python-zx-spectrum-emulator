package sk.zoliky.logic

import sk.zoliky.model.Card
import sk.zoliky.model.Rank
import sk.zoliky.model.Suit

/**
 * Validates card combinations and calculates points according to Žolíky rules.
 * Ověřuje kombinace karet a počítá body podle pravidel Žolíků.
 */
class CombinationValidator {

    /**
     * Checks if the cards form a valid set (group of same rank, different suits).
     * 3 or 4 cards.
     * Kontroluje, zda karty tvoří platnou skupinu (stejná hodnota, různé barvy).
     * 3 nebo 4 karty.
     */
    fun isValidSet(cards: List<Card>): Boolean {
        if (cards.size !in 3..4) return false

        val nonJokers = cards.filter { !it.isJoker() }

        // If all are jokers, it's valid (though rare strategy)
        if (nonJokers.isEmpty()) return true

        // All non-jokers must have the same rank
        val firstRank = nonJokers.first().rank
        if (nonJokers.any { it.rank != firstRank }) return false

        // All non-jokers must have distinct suits
        val suits = nonJokers.map { it.suit }
        if (suits.size != suits.toSet().size) return false

        return true
    }

    /**
     * Checks if the cards form a valid sequence (same suit, consecutive ranks).
     * At least 3 cards.
     * Kontroluje, zda karty tvoří platnou postupku (stejná barva, po sobě jdoucí hodnoty).
     * Alespoň 3 karty.
     */
    fun isValidSequence(cards: List<Card>): Boolean {
        if (cards.size < 3) return false

        val nonJokers = cards.filter { !it.isJoker() }
        
        // If 0 or 1 non-joker, it's always valid sequence if we assume jokers can be anything needed
        // But we usually need to define suit. If all jokers, technically valid but ambiguous suit.
        // Rule: Must be able to form a sequence.
        if (nonJokers.isEmpty()) return true
        if (nonJokers.size == 1) return true

        // All non-jokers must have the same suit
        val firstSuit = nonJokers.first().suit
        if (nonJokers.any { it.suit != firstSuit }) return false

        // Sort non-jokers by rank index for easier checking
        // Special handling for Ace: It can be low (before 2) or high (after K)
        // We need to check if a valid sequence can be formed considering Jokers
        
        // Strategy: Try Ace as low (1), then try Ace as high (14).
        // If either is valid, return true.
        // Optimization: If no Ace, just check standard.
        
        if (nonJokers.any { it.rank == Rank.ACE }) {
            return checkSequenceWithValues(cards, treatAceAsLow = true) || 
                   checkSequenceWithValues(cards, treatAceAsLow = false)
        } else {
            return checkSequenceWithValues(cards, treatAceAsLow = false)
        }
    }

    private fun checkSequenceWithValues(cards: List<Card>, treatAceAsLow: Boolean): Boolean {
        // Map cards to values. Jokers are null placeholders we need to fill.
        // We only care about the relative gaps between non-jokers.
        
        val sortedCardsWithIndices = cards.sortedBy { 
            if (it.isJoker()) Int.MAX_VALUE else getRankValue(it.rank, treatAceAsLow) 
        }
        
        val nonJokers = sortedCardsWithIndices.filter { !it.isJoker() }
        val jokerCount = cards.size - nonJokers.size

        if (nonJokers.isEmpty()) return true
        
        // Check gaps between consecutive non-jokers
        var jokersNeeded = 0
        for (i in 0 until nonJokers.size - 1) {
            val currentVal = getRankValue(nonJokers[i].rank, treatAceAsLow)
            val nextVal = getRankValue(nonJokers[i+1].rank, treatAceAsLow)
            
            // If strictly decreasing or same (duplicate card value in sequence), invalid
            // Unless it is the same card instance? No, assuming distinct cards.
            // Duplicate rank in sequence implies invalid (e.g. 7H, 7H) - but we checked suit already.
            // If same suit and same rank, it's duplicate card (cheat or multi-deck issue).
            // Invalid for sequence.
            if (nextVal <= currentVal) return false
            
            val gap = nextVal - currentVal - 1
            jokersNeeded += gap
        }

        return jokersNeeded <= jokerCount
    }

    private fun getRankValue(rank: Rank, aceLow: Boolean): Int {
        return when (rank) {
            Rank.TWO -> 2
            Rank.THREE -> 3
            Rank.FOUR -> 4
            Rank.FIVE -> 5
            Rank.SIX -> 6
            Rank.SEVEN -> 7
            Rank.EIGHT -> 8
            Rank.NINE -> 9
            Rank.TEN -> 10
            Rank.JACK -> 11
            Rank.QUEEN -> 12
            Rank.KING -> 13
            Rank.ACE -> if (aceLow) 1 else 14
            Rank.JOKER -> 0 // Should not happen in this context
        }
    }

    /**
     * Calculates the point value of a valid combination.
     * Returns 0 if invalid.
     * Počítá bodovou hodnotu platné kombinace.
     * Vrací 0, pokud je neplatná.
     */
    fun calculatePoints(cards: List<Card>): Int {
        if (isValidSet(cards)) {
            // In a set, points are sum of values.
            // Jokers take rank of the set.
            // If all jokers, assume highest possible? usually A (10pts).
            // Rules say: Joker replaces card.
            // Aces in set are 10 points.
            
            val nonJoker = cards.firstOrNull { !it.isJoker() }
            val rank = nonJoker?.rank ?: Rank.ACE // Default to Ace if all jokers
            
            val pointsPerCard = when (rank) {
                Rank.ACE -> 10
                Rank.JOKER -> 10 // Fallback
                Rank.JACK, Rank.QUEEN, Rank.KING, Rank.TEN -> 10
                else -> rank.value
            }
            
            return cards.size * pointsPerCard
        }
        
        if (isValidSequence(cards)) {
            // Sequence points:
            // Sum of individual cards.
            // Joker takes value of replaced card.
            // Ace: 1 in low seq, 11 in high seq.
            
            // We need to reconstruct the sequence to assign values to Jokers.
            // Heuristic: Use the validation logic again to find the best arrangement?
            // Or just simpler logic:
            
            return calculateSequencePoints(cards)
        }
        
        return 0
    }

    private fun calculateSequencePoints(cards: List<Card>): Int {
        val nonJokers = cards.filter { !it.isJoker() }
        if (nonJokers.isEmpty()) {
            // All jokers? Rare. Assume A-2-3... or Q-K-A?
            // Maximize points? Usually A(11)+K(10)+Q(10) = 31.
            // Let's assume best case for player.
            // For 3 jokers: 30 points (10+10+10)? No, Joker takes value.
            // If it replaces Q,K,A it is 10+10+11.
            // Simplification: In pure joker sequence, ambiguous.
            // Let's return 0 or standard assumption.
            // Given "Initial Meld" checks min points, let's assume High values.
            // But let's verify if Ace can be low/high.
            return cards.size * 10 // Approximate avg high?
            // Actually, let's play safe.
        }

        // Determine if Ace is High or Low based on neighbors
        val hasAce = nonJokers.any { it.rank == Rank.ACE }
        var isHighAce = false
        if (hasAce) {
            // If other cards are high (>= 10), assume high.
            // If other cards are low (<= 5), assume low.
            // If only Ace and Jokers, ambiguous.
            // Check validation to confirm.
             if (checkSequenceWithValues(cards, treatAceAsLow = false)) {
                 isHighAce = true
             }
             // If both valid, usually High gives more points, prefer High.
        }
        
        // Reconstruct sequence
        // Find the "start" value of the sequence
        // We know nonJokers are in order.
        // We need to find the rank of the first card in the visual sequence.
        
        // Map nonJokers to their values
        val sorted = nonJokers.sortedBy { getRankValue(it.rank, !isHighAce) }
        val firstNonJoker = sorted.first()
        val firstNonJokerValue = getRankValue(firstNonJoker.rank, !isHighAce)
        
        // Count jokers before first non-joker (this is tricky because we don't know order in list,
        // but it's a "hand" or "meld" list. Usually sorted?
        // Actually for calculating points logic doesn't care about list order, but Logic VALIDITY checks continuity.
        // In a valid sequence, the cards populate a range [min, max].
        // Range size = cards.size.
        // Any gaps in nonJokers are filled by Jokers.
        // Leftover Jokers extend range.
        // To maximize points, extend towards higher values?
        // Rules usually say "Joker replaces specific card".
        // But here we just have a list.
        
        // We assume the range is defined by [firstNonJokerValue - jokersBefore, lastNonJokerValue + jokersAfter].
        // But we don't know distribution of jokers.
        // Example: J, 5, 7.  J could be 6 (5,6,7) points=5+6+7=18.
        // Example: J, 5, 6.  J could be 4 (4,5,6) or 7 (5,6,7). 7 is more points.
        // Strategy: Maximize points.
        
        val minVal = sorted.first().let { getRankValue(it.rank, !isHighAce) }
        val maxVal = sorted.last().let { getRankValue(it.rank, !isHighAce) }
        
        val span = maxVal - minVal + 1
        val filledRangePoints = (minVal..maxVal).sumOf { rankVal ->
             getPointValue(rankVal)
        }
        
        // Remaining jokers count
        val totalJokers = cards.size - nonJokers.size
        val jokersUsedInside = span - nonJokers.size
        val jokersFloating = totalJokers - jokersUsedInside
        
        var currentPoints = filledRangePoints
        
        // Distribute floating jokers to maximize points (add to top if possible)
        var upperBoundary = maxVal
        var lowerBoundary = minVal
        
        repeat(jokersFloating) {
            // Try adding to top
            val nextUp = upperBoundary + 1
            val pointsUp = if (isValidRankValue(nextUp)) getPointValue(nextUp) else -1
            
            // Try adding to bottom
            val nextDown = lowerBoundary - 1
            val pointsDown = if (isValidRankValue(nextDown)) getPointValue(nextDown) else -1
            
            if (pointsUp >= pointsDown && pointsUp != -1) {
                currentPoints += pointsUp
                upperBoundary++
            } else if (pointsDown != -1) {
                currentPoints += pointsDown
                lowerBoundary--
            } else {
                // Neither valid? (e.g. sequence is full 2..A)
                // Should not happen with 108 cards limit but theoretically constraint.
            }
        }
        
        return currentPoints
    }
    
    // Convert 1..14 scale back to points
    private fun getPointValue(rankVal: Int): Int {
        return when (rankVal) {
            1 -> 1 // Low Ace
            14 -> 11 // High Ace
            11, 12, 13 -> 10 // J, Q, K
            else -> rankVal // 2..10 -> face value (10 -> 10)
        }
    }
    
    private fun isValidRankValue(rankVal: Int): Boolean {
        return rankVal in 1..14
    }
}
