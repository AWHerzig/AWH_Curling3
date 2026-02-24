import pandas as pd
import numpy as np

class CurlingShotScorer:
    """
    Scores potential curling shots based on effectiveness and risk.
    
    Assumes a coordinate system where:
    - Button is at (button_x, button_y)
    - Stones DataFrame has columns: 'x', 'y', 'team' (0 or 1)
    """
    
    def __init__(self, stones_df, button_x, button_y, stones_remaining, 
                 current_end, max_curl, my_team=0, has_hammer=True):
        """
        Initialize the shot scorer.
        
        Parameters:
        -----------
        stones_df : DataFrame with columns ['x', 'y', 'team']
        button_x, button_y : float - coordinates of the button (center)
        stones_remaining : int - stones left to play this end
        current_end : int - which end (1-10 typically)
        max_curl : float - maximum curl distance possible
        my_team : int - which team the AI is (0 or 1)
        has_hammer : bool - whether AI has last stone advantage
        """
        self.stones = stones_df.copy()
        self.button_x = button_x
        self.button_y = button_y
        self.stones_remaining = stones_remaining
        self.current_end = current_end
        self.max_curl = max_curl
        self.my_team = my_team
        self.has_hammer = has_hammer
        
    def distance_to_button(self, x, y):
        """Calculate Euclidean distance from a point to the button."""
        return np.sqrt((x - self.button_x)**2 + (y - self.button_y)**2)
    
    def score_draw_shot(self, target_x, target_y):
        """
        Score a draw shot (placing a stone at target position).
        
        Returns: (effectiveness_score, risk_score)
        """
        # Effectiveness based on distance to button
        dist_to_button = self.distance_to_button(target_x, target_y)
        
        # Normalize: closer is better (assume house radius ~1.83m, use 2.5m as reference)
        effectiveness = max(0, 100 - (dist_to_button / 2.5) * 100)
        
        # Bonus if this would be closest to button
        if len(self.stones) > 0:
            opponent_stones = self.stones[self.stones['team'] != self.my_team]
            if len(opponent_stones) > 0:
                closest_opponent_dist = opponent_stones.apply(
                    lambda row: self.distance_to_button(row['x'], row['y']), 
                    axis=1
                ).min()
                if dist_to_button < closest_opponent_dist:
                    effectiveness += 30  # Bonus for being shot stone
        
        # Check if position is guarded (protected by stones in front)
        guarded = self._is_position_guarded(target_x, target_y, self.my_team)
        if guarded:
            effectiveness += 20
        
        # Risk factors
        risk = 0
        
        # Distance-based risk (harder to hit exact spots far from button)
        risk += min(40, dist_to_button * 10)
        
        # Curl complexity (how much curl needed)
        curl_needed = abs(target_x - self.button_x)
        curl_risk = (curl_needed / self.max_curl) * 30
        risk += curl_risk
        
        # Crowded house increases risk of hitting other stones
        stones_in_house = len(self.stones[
            self.stones.apply(lambda row: self.distance_to_button(row['x'], row['y']) < 1.83, axis=1)
        ])
        risk += stones_in_house * 5
        
        return (min(100, effectiveness), min(100, risk))
    
    def score_guard_shot(self, guard_x, guard_y, protects_stone_idx=None):
        """
        Score a guard shot (placing a stone in front to protect).
        
        Parameters:
        -----------
        guard_x, guard_y : position of the guard
        protects_stone_idx : optional index of stone being protected
        """
        effectiveness = 50  # Base value for guards
        
        # Check if we have stones worth protecting
        my_stones = self.stones[self.stones['team'] == self.my_team]
        if len(my_stones) > 0:
            # Guards are more valuable if protecting stones close to button
            closest_my_stone_dist = my_stones.apply(
                lambda row: self.distance_to_button(row['x'], row['y']), 
                axis=1
            ).min()
            
            if closest_my_stone_dist < 1.0:
                effectiveness += 30
            elif closest_my_stone_dist < 1.83:
                effectiveness += 15
        
        # Center guards are more valuable
        center_offset = abs(guard_x - self.button_x)
        if center_offset < 0.3:
            effectiveness += 20
        
        # Strategic timing: guards better early in end
        if self.stones_remaining > 10:
            effectiveness += 10
        
        # Risk assessment
        risk = 25  # Base risk for guards
        
        # Guards need good weight control
        risk += 15
        
        # Curl complexity
        curl_needed = abs(guard_x - self.button_x)
        risk += (curl_needed / self.max_curl) * 20
        
        return (min(100, effectiveness), min(100, risk))
    
    def score_takeout_shot(self, target_stone_idx, hit_weight='normal'):
        """
        Score a takeout shot (removing an opponent's stone).
        
        Parameters:
        -----------
        target_stone_idx : index in stones_df of stone to remove
        hit_weight : 'normal', 'hack' (hard), or 'soft'
        """
        if target_stone_idx >= len(self.stones):
            return (0, 100)
        
        target = self.stones.iloc[target_stone_idx]
        
        # Only take out opponent stones
        if target['team'] == self.my_team:
            return (0, 100)
        
        # Effectiveness based on target's proximity to button
        target_dist = self.distance_to_button(target['x'], target['y'])
        
        # Removing stones close to button is highly valuable
        if target_dist < 0.5:
            effectiveness = 90
        elif target_dist < 1.0:
            effectiveness = 75
        elif target_dist < 1.83:  # In the house
            effectiveness = 60
        else:
            effectiveness = 30  # Removing guards
        
        # Bonus if this is currently the shot stone (closest to button)
        opponent_stones = self.stones[self.stones['team'] != self.my_team]
        if len(opponent_stones) > 0:
            closest_opponent_idx = opponent_stones.apply(
                lambda row: self.distance_to_button(row['x'], row['y']), 
                axis=1
            ).idxmin()
            if closest_opponent_idx == target_stone_idx:
                effectiveness += 20
        
        # Risk assessment
        risk = 35  # Base risk for takeouts
        
        # Weight-based risk
        if hit_weight == 'hack':
            risk += 25  # Hard hits are less predictable
        elif hit_weight == 'soft':
            risk += 10
        else:
            risk += 15
        
        # Angle and curl complexity
        curl_needed = abs(target['x'] - self.button_x)
        risk += (curl_needed / self.max_curl) * 25
        
        # Risk of wrecking our own stones
        my_stones = self.stones[self.stones['team'] == self.my_team]
        nearby_my_stones = my_stones[
            my_stones.apply(
                lambda row: np.sqrt((row['x'] - target['x'])**2 + (row['y'] - target['y'])**2) < 0.5,
                axis=1
            )
        ]
        risk += len(nearby_my_stones) * 10
        
        return (min(100, effectiveness), min(100, risk))
    
    def score_freeze_shot(self, target_stone_idx):
        """
        Score a freeze shot (placing stone directly against opponent's stone).
        """
        if target_stone_idx >= len(self.stones):
            return (0, 100)
        
        target = self.stones.iloc[target_stone_idx]
        target_dist = self.distance_to_button(target['x'], target['y'])
        
        # Freezes most effective on opponent stones close to button
        if target_dist < 1.0:
            effectiveness = 85
        elif target_dist < 1.83:
            effectiveness = 65
        else:
            effectiveness = 30
        
        # Freeze is defensive, better when opponent has hammer
        if not self.has_hammer:
            effectiveness += 15
        
        # Risk: freezes are very difficult shots
        risk = 70  # High base risk
        
        # Even harder if the stone is well-guarded
        if self._is_position_guarded(target['x'], target['y'], target['team']):
            risk += 20
        
        return (min(100, effectiveness), min(100, risk))
    
    def _is_position_guarded(self, x, y, team):
        """Check if a position is protected by guards in front of it."""
        # Simplified: check if there are stones of same team closer to throwing line
        # (assuming y increases toward button)
        guards = self.stones[
            (self.stones['team'] == team) & 
            (self.stones['y'] < y) &  # In front
            (abs(self.stones['x'] - x) < 0.5)  # Close to same line
        ]
        return len(guards) > 0
    
    def generate_and_score_shots(self, num_draws=5, num_guards=3):
        """
        Generate a list of possible shots and score each.
        
        Returns: List of dicts with shot info and scores
        """
        shots = []
        
        # Generate draw shots (positions in and around the house)
        for i in range(num_draws):
            angle = (i / num_draws) * 2 * np.pi
            # Vary radius from button
            for radius in [0.3, 0.8, 1.5]:
                target_x = self.button_x + radius * np.cos(angle)
                target_y = self.button_y + radius * np.sin(angle)
                
                eff, risk = self.score_draw_shot(target_x, target_y)
                shots.append({
                    'type': 'draw',
                    'target_x': target_x,
                    'target_y': target_y,
                    'effectiveness': eff,
                    'risk': risk
                })
        
        # Generate guard shots
        for i in range(num_guards):
            guard_x = self.button_x + (i - num_guards/2) * 0.4
            guard_y = self.button_y - 2.0  # In front of house
            
            eff, risk = self.score_guard_shot(guard_x, guard_y)
            shots.append({
                'type': 'guard',
                'target_x': guard_x,
                'target_y': guard_y,
                'effectiveness': eff,
                'risk': risk
            })
        
        # Generate takeout shots for all opponent stones
        opponent_stones = self.stones[self.stones['team'] != self.my_team]
        for idx in opponent_stones.index:
            for weight in ['normal', 'hack']:
                eff, risk = self.score_takeout_shot(idx, weight)
                target = self.stones.iloc[idx]
                shots.append({
                    'type': 'takeout',
                    'target_stone': idx,
                    'target_x': target['x'],
                    'target_y': target['y'],
                    'weight': weight,
                    'effectiveness': eff,
                    'risk': risk
                })
        
        # Generate freeze shots
        for idx in opponent_stones.index:
            eff, risk = self.score_freeze_shot(idx)
            target = self.stones.iloc[idx]
            shots.append({
                'type': 'freeze',
                'target_stone': idx,
                'target_x': target['x'],
                'target_y': target['y'],
                'effectiveness': eff,
                'risk': risk
            })
        
        return shots
    
    def select_best_shot(self, shots, risk_weight=0.4):
        """
        Select the best shot from a list using a combined score.
        
        Parameters:
        -----------
        shots : list of shot dictionaries from generate_and_score_shots
        risk_weight : float (0-1), how much to penalize risk
        
        Returns: best shot dictionary
        """
        for shot in shots:
            # Combined score: effectiveness reduced by risk
            shot['combined_score'] = shot['effectiveness'] * (1 - risk_weight * (shot['risk'] / 100))
        
        # Sort by combined score
        shots_sorted = sorted(shots, key=lambda s: s['combined_score'], reverse=True)
        
        return shots_sorted[0] if shots_sorted else None


# Example usage
if __name__ == "__main__":
    # Create sample game state
    stones_data = pd.DataFrame({
        'x': [0.5, -0.3, 0.8, -0.5],
        'y': [0.2, 0.5, -0.3, 1.0],
        'team': [0, 1, 1, 0]  # 0 = my team, 1 = opponent
    })
    
    button_x, button_y = 0.0, 0.0
    stones_remaining = 12
    current_end = 3
    max_curl = 1.5
    
    # Initialize scorer
    scorer = CurlingShotScorer(
        stones_df=stones_data,
        button_x=button_x,
        button_y=button_y,
        stones_remaining=stones_remaining,
        current_end=current_end,
        max_curl=max_curl,
        my_team=0,
        has_hammer=True
    )
    
    # Generate and score all possible shots
    shots = scorer.generate_and_score_shots()
    
    # Select best shot
    best_shot = scorer.select_best_shot(shots, risk_weight=0.35)
    
    print(f"Best shot recommended:")
    print(f"Type: {best_shot['type']}")
    print(f"Target: ({best_shot['target_x']:.2f}, {best_shot['target_y']:.2f})")
    print(f"Effectiveness: {best_shot['effectiveness']:.1f}")
    print(f"Risk: {best_shot['risk']:.1f}")
    print(f"Combined Score: {best_shot['combined_score']:.1f}")
    
    print(f"\nTop 5 shots:")
    shots_sorted = sorted(shots, key=lambda s: s['combined_score'], reverse=True)
    for i, shot in enumerate(shots_sorted[:5]):
        print(f"{i+1}. {shot['type']:10s} - Eff: {shot['effectiveness']:5.1f}, Risk: {shot['risk']:5.1f}, Score: {shot['combined_score']:5.1f}")
