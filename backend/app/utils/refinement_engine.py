# backend/app/utils/refinement_engine.py
import google.generativeai as genai
import json
import re
from typing import Dict, Any, List
from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class RefinementEngine:
    """Interactive scope refinement with intent detection and automatic recalculation"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Intent patterns
        self.intent_patterns = {
            'modify_tasks': ['add', 'remove', 'include', 'exclude', 'add task', 'remove activity'],
            'adjust_timeline': ['shorter', 'longer', 'reduce time', 'extend', 'faster', 'quicker', 'weeks', 'months'],
            'apply_discount': ['discount', 'reduce cost', 'reduce price', '% off', 'percent off'],
            'modify_resources': ['add developer', 'remove', 'more team', 'less team', 'increase headcount']
        }
    
    async def process_refinement_request(self, user_message: str, current_scope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process refinement request and update scope
        
        Args:
            user_message: User's refinement request
            current_scope: Current scope data
            
        Returns:
            Dict with updated_scope, response, changes_made, intent
        """
        try:
            # Detect intent
            intent = self._detect_intent(user_message)
            
            # Process based on intent
            if intent == 'modify_tasks':
                return await self._modify_tasks(user_message, current_scope)
            elif intent == 'adjust_timeline':
                return await self._adjust_timeline(user_message, current_scope)
            elif intent == 'apply_discount':
                return await self._apply_discount(user_message, current_scope)
            elif intent == 'modify_resources':
                return await self._modify_resources(user_message, current_scope)
            else:
                return await self._generic_refinement(user_message, current_scope)
                
        except Exception as e:
            print(f"❌ Refinement error: {e}")
            return {
                'updated_scope': current_scope,
                'response': f"I encountered an error: {str(e)}. Please try rephrasing your request.",
                'changes_made': [],
                'intent': 'error'
            }
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message"""
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        return 'generic'
    
    async def _modify_tasks(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Add or remove tasks/activities"""
        
        prompt = f"""
Analyze this request to modify project activities:
User Request: "{message}"

Current Activities: {json.dumps(scope.get('activities', [])[:5], indent=2)}

Determine:
1. Should we ADD or REMOVE activities?
2. What specific activities should be affected?
3. What phase should they be in?

Return ONLY JSON:
{{
  "action": "add" or "remove",
  "activity_type": "description of activity",
  "phase": "phase name",
  "effort_days": estimated days (if adding)
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            instruction = self._parse_json_response(response.text)
            
            updated_scope = scope.copy()
            activities = updated_scope.get('activities', [])
            
            if instruction['action'] == 'add':
                # Add new activity
                new_activity = {
                    'name': instruction['activity_type'],
                    'phase': instruction.get('phase', 'Development'),
                    'effort_days': instruction.get('effort_days', 5),
                    'dependencies': [],
                    'resources_needed': ['Developer']
                }
                activities.append(new_activity)
                changes = [f"Added: {new_activity['name']} ({new_activity['effort_days']} days)"]
                
            else:  # remove
                # Remove matching activities
                original_count = len(activities)
                activities = [
                    a for a in activities 
                    if instruction['activity_type'].lower() not in a['name'].lower()
                ]
                removed_count = original_count - len(activities)
                changes = [f"Removed {removed_count} activity(ies) matching '{instruction['activity_type']}'"]
            
            updated_scope['activities'] = activities
            
            # Recalculate timeline
            updated_scope = self._recalculate_timeline(updated_scope)
            
            return {
                'updated_scope': updated_scope,
                'response': f"I've {instruction['action']}ed activities as requested. {changes[0]}",
                'changes_made': changes,
                'intent': 'modify_tasks'
            }
            
        except Exception as e:
            print(f"Error in _modify_tasks: {e}")
            return {
                'updated_scope': scope,
                'response': "I couldn't modify the tasks. Please be more specific.",
                'changes_made': [],
                'intent': 'modify_tasks'
            }
    
    async def _adjust_timeline(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust project timeline"""
        
        # Extract time adjustment
        message_lower = message.lower()
        
        if 'shorter' in message_lower or 'faster' in message_lower or 'quicker' in message_lower:
            adjustment_factor = 0.85  # 15% shorter
            direction = "shorter"
        elif 'longer' in message_lower or 'extend' in message_lower:
            adjustment_factor = 1.15  # 15% longer
            direction = "longer"
        else:
            # Try to extract specific duration
            weeks_match = re.search(r'(\d+)\s*weeks?', message_lower)
            if weeks_match:
                target_weeks = int(weeks_match.group(1))
                current_weeks = sum(p.get('duration_weeks', 0) for p in scope.get('timeline', {}).get('phases', []))
                adjustment_factor = target_weeks / current_weeks if current_weeks > 0 else 1.0
                direction = "adjusted"
            else:
                adjustment_factor = 1.0
                direction = "unchanged"
        
        updated_scope = scope.copy()
        timeline = updated_scope.get('timeline', {})
        phases = timeline.get('phases', [])
        
        # Adjust phase durations
        current_week = 1
        for phase in phases:
            original_duration = phase.get('duration_weeks', 4)
            new_duration = max(1, int(original_duration * adjustment_factor))
            phase['duration_weeks'] = new_duration
            phase['start_week'] = current_week
            phase['end_week'] = current_week + new_duration - 1
            current_week += new_duration
        
        # Update total duration
        total_weeks = sum(p['duration_weeks'] for p in phases)
        timeline['total_duration_months'] = round(total_weeks / 4.33, 1)
        
        updated_scope['timeline'] = timeline
        
        # Recalculate resources based on new timeline
        updated_scope = self._recalculate_resources(updated_scope)
        
        changes = [
            f"Timeline made {direction}",
            f"Total duration: {timeline['total_duration_months']} months",
            f"Total weeks: {total_weeks}"
        ]
        
        return {
            'updated_scope': updated_scope,
            'response': f"I've made the timeline {direction}. New duration: {timeline['total_duration_months']} months.",
            'changes_made': changes,
            'intent': 'adjust_timeline'
        }
    
    async def _apply_discount(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Apply discount to project cost"""
        
        # Extract discount percentage
        discount_match = re.search(r'(\d+)\s*%', message)
        if discount_match:
            discount_percent = int(discount_match.group(1))
        else:
            discount_percent = 10  # Default 10%
        
        updated_scope = scope.copy()
        resources = updated_scope.get('resources', [])
        
        discount_factor = 1 - (discount_percent / 100)
        
        # Apply discount to all resources
        for resource in resources:
            original_cost = resource.get('total_cost', 0)
            resource['total_cost'] = round(original_cost * discount_factor, 2)
        
        updated_scope['resources'] = resources
        
        # Recalculate cost breakdown
        total_cost = sum(r.get('total_cost', 0) for r in resources)
        cost_breakdown = updated_scope.get('cost_breakdown', {})
        cost_breakdown['total_cost'] = total_cost
        cost_breakdown['discount_applied'] = discount_percent
        cost_breakdown['contingency_amount'] = round(
            total_cost * (cost_breakdown.get('contingency_percentage', 15) / 100),
            2
        )
        
        updated_scope['cost_breakdown'] = cost_breakdown
        
        changes = [
            f"Applied {discount_percent}% discount",
            f"New total cost: ${total_cost:,.2f}",
            f"Savings: ${sum(r.get('total_cost', 0) for r in scope.get('resources', [])) - total_cost:,.2f}"
        ]
        
        return {
            'updated_scope': updated_scope,
            'response': f"I've applied a {discount_percent}% discount. New total: ${total_cost:,.2f}",
            'changes_made': changes,
            'intent': 'apply_discount'
        }
    
    async def _modify_resources(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Add or remove resources"""
        
        message_lower = message.lower()
        
        # Detect role and action
        role_keywords = {
            'frontend': 'Frontend Developer',
            'backend': 'Backend Developer',
            'designer': 'UI/UX Designer',
            'qa': 'QA Engineer',
            'devops': 'DevOps Engineer',
            'pm': 'Project Manager',
            'analyst': 'Business Analyst'
        }
        
        detected_role = None
        for keyword, role_name in role_keywords.items():
            if keyword in message_lower:
                detected_role = role_name
                break
        
        if not detected_role:
            detected_role = 'Developer'  # Default
        
        # Detect count
        count_match = re.search(r'(\d+)', message)
        count_change = int(count_match.group(1)) if count_match else 1
        
        # Detect add or remove
        is_adding = any(word in message_lower for word in ['add', 'more', 'increase'])
        
        updated_scope = scope.copy()
        resources = updated_scope.get('resources', [])
        
        # Find existing resource
        existing_resource = next((r for r in resources if r['role'] == detected_role), None)
        
        changes = []
        
        if existing_resource:
            if is_adding:
                existing_resource['count'] += count_change
                existing_resource['total_cost'] = (
                    existing_resource['count'] * 
                    existing_resource['effort_months'] * 
                    existing_resource['monthly_rate']
                )
                changes.append(f"Added {count_change} {detected_role}(s)")
            else:
                existing_resource['count'] = max(0, existing_resource['count'] - count_change)
                existing_resource['total_cost'] = (
                    existing_resource['count'] * 
                    existing_resource['effort_months'] * 
                    existing_resource['monthly_rate']
                )
                changes.append(f"Removed {count_change} {detected_role}(s)")
        else:
            # Add new resource
            if is_adding:
                new_resource = {
                    'role': detected_role,
                    'count': count_change,
                    'effort_months': 3,
                    'allocation_percentage': 100,
                    'monthly_rate': 8000,
                    'total_cost': count_change * 3 * 8000
                }
                resources.append(new_resource)
                changes.append(f"Added {count_change} new {detected_role}(s)")
        
        updated_scope['resources'] = resources
        
        # Recalculate total cost
        total_cost = sum(r.get('total_cost', 0) for r in resources)
        cost_breakdown = updated_scope.get('cost_breakdown', {})
        cost_breakdown['total_cost'] = total_cost
        cost_breakdown['contingency_amount'] = round(
            total_cost * (cost_breakdown.get('contingency_percentage', 15) / 100),
            2
        )
        updated_scope['cost_breakdown'] = cost_breakdown
        
        changes.append(f"New total cost: ${total_cost:,.2f}")
        
        return {
            'updated_scope': updated_scope,
            'response': f"I've updated the team. {changes[0]}. New total: ${total_cost:,.2f}",
            'changes_made': changes,
            'intent': 'modify_resources'
        }
    
    async def _generic_refinement(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic refinement requests"""
        
        prompt = f"""
User wants to refine the project scope. 

User Request: "{message}"

Current Scope Summary:
- Total Duration: {scope.get('timeline', {}).get('total_duration_months', 0)} months
- Total Cost: ${scope.get('cost_breakdown', {}).get('total_cost', 0):,.2f}
- Activities: {len(scope.get('activities', []))}
- Resources: {len(scope.get('resources', []))}

Provide a helpful response explaining what changes can be made. Be specific and actionable.
Return ONLY plain text response (no JSON).
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            return {
                'updated_scope': scope,
                'response': response.text.strip(),
                'changes_made': ['No automatic changes made - awaiting specific instruction'],
                'intent': 'generic'
            }
            
        except Exception as e:
            return {
                'updated_scope': scope,
                'response': "I understand you'd like to refine the scope. Could you be more specific? For example: 'Make timeline 2 weeks shorter' or 'Add security testing' or 'Apply 10% discount'",
                'changes_made': [],
                'intent': 'generic'
            }
    
    def _recalculate_timeline(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Recalculate timeline based on activities"""
        activities = scope.get('activities', [])
        total_effort_days = sum(a.get('effort_days', 0) for a in activities)
        
        # Rough estimate: assume 5-day weeks and parallel work
        estimated_weeks = max(1, int(total_effort_days / 5 / 3))  # Assuming 3 parallel streams
        
        timeline = scope.get('timeline', {})
        timeline['total_duration_months'] = round(estimated_weeks / 4.33, 1)
        
        scope['timeline'] = timeline
        return scope
    
    def _recalculate_resources(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Recalculate resource costs based on timeline"""
        timeline = scope.get('timeline', {})
        total_months = timeline.get('total_duration_months', 6)
        
        resources = scope.get('resources', [])
        for resource in resources:
            # Adjust effort_months based on new timeline
            resource['effort_months'] = min(
                total_months,
                resource.get('effort_months', total_months)
            )
            resource['total_cost'] = (
                resource['count'] * 
                resource['effort_months'] * 
                resource['monthly_rate']
            )
        
        # Recalculate total cost
        total_cost = sum(r['total_cost'] for r in resources)
        cost_breakdown = scope.get('cost_breakdown', {})
        cost_breakdown['total_cost'] = total_cost
        cost_breakdown['contingency_amount'] = round(
            total_cost * (cost_breakdown.get('contingency_percentage', 15) / 100),
            2
        )
        
        scope['resources'] = resources
        scope['cost_breakdown'] = cost_breakdown
        
        return scope
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        try:
            # Remove markdown code blocks
            text = re.sub(r'```json\s*', '', response_text)
            text = re.sub(r'```\s*', '', text).strip()
            
            # Find JSON object
            start = text.find('{')
            end = text.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
                
        except Exception as e:
            print(f"JSON parsing error: {e}")
            raise


# Global instance
refinement_engine = RefinementEngine()