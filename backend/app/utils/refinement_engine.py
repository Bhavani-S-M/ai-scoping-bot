# backend/app/utils/refinement_engine.py
import google.generativeai as genai
import json
import re
import math
from typing import Dict, Any, List, Tuple
from app.config.config import settings
from app.schemas.project_schemas import RefinementIntent

genai.configure(api_key=settings.GEMINI_API_KEY)

class RefinementEngine:
    """Enhanced interactive scope refinement with advanced NLP intent detection"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        # Enhanced intent patterns with weights
        self.intent_patterns = {
            'modify_tasks': {
                'patterns': ['add task', 'remove activity', 'include', 'exclude', 'new feature', 'additional work'],
                'weight': 0.9
            },
            'adjust_timeline': {
                'patterns': ['shorter', 'longer', 'reduce time', 'extend', 'faster', 'quicker', 'weeks', 'months', 'duration'],
                'weight': 0.8
            },
            'apply_discount': {
                'patterns': ['discount', 'reduce cost', 'reduce price', '% off', 'percent off', 'cheaper', 'lower price'],
                'weight': 0.7
            },
            'modify_resources': {
                'patterns': ['add developer', 'remove resource', 'more team', 'less team', 'increase headcount', 'reduce team'],
                'weight': 0.8
            }
        }
    
    async def process_refinement_request(self, user_message: str, current_scope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced refinement processing with better NLP and constraint validation
        """
        try:
            # Detect intent with confidence scoring
            intent, confidence = self._detect_intent_with_confidence(user_message)
            
            # Process based on intent
            if intent == RefinementIntent.MODIFY_TASKS and confidence > 0.6:
                return await self._modify_tasks(user_message, current_scope)
            elif intent == RefinementIntent.ADJUST_TIMELINE and confidence > 0.6:
                return await self._adjust_timeline(user_message, current_scope)
            elif intent == RefinementIntent.APPLY_DISCOUNT and confidence > 0.7:
                return await self._apply_discount(user_message, current_scope)
            elif intent == RefinementIntent.MODIFY_RESOURCES and confidence > 0.6:
                return await self._modify_resources(user_message, current_scope)
            else:
                return await self._generic_refinement(user_message, current_scope, intent)
                
        except Exception as e:
            print(f"❌ Refinement error: {e}")
            return {
                'updated_scope': current_scope,
                'response': f"I encountered an error: {str(e)}. Please try rephrasing your request.",
                'changes_made': ['Error occurred - no changes applied'],
                'intent': RefinementIntent.ERROR
            }
    
    def _detect_intent_with_confidence(self, message: str) -> Tuple[RefinementIntent, float]:
        """Enhanced intent detection with confidence scoring"""
        message_lower = message.lower()
        scores = {}
        
        for intent, data in self.intent_patterns.items():
            score = 0
            for pattern in data['patterns']:
                if pattern in message_lower:
                    score += data['weight']
            
            # Boost score for exact matches
            if any(f" {pattern} " in f" {message_lower} " for pattern in data['patterns']):
                score += 0.2
                
            scores[intent] = score
        
        # Get best intent
        if scores:
            best_intent = max(scores, key=scores.get)
            confidence = min(1.0, scores[best_intent])
            return RefinementIntent(best_intent), confidence
        
        return RefinementIntent.GENERIC, 0.5
    
    async def _modify_tasks(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced task modification with phase awareness"""
        
        prompt = f"""
Analyze this task modification request and provide structured instructions:

User Request: "{message}"

Current Activities (first 10): 
{json.dumps([{'name': a.get('name'), 'phase': a.get('phase'), 'effort_days': a.get('effort_days')} 
              for a in scope.get('activities', [])[:10]], indent=2)}

Determine:
1. Action: "add" or "remove" or "modify"
2. Activity details (name, description if adding)
3. Target phase
4. Estimated effort in days
5. Dependencies (if any)

Return ONLY valid JSON:
{{
  "action": "add|remove|modify",
  "activity_name": "specific activity name",
  "activity_description": "detailed description if adding",
  "target_phase": "Planning|Design|Development|Testing|Deployment",
  "effort_days": number,
  "dependencies": ["list of prerequisite activities"],
  "resources_required": ["list of required roles"]
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            instruction = self._parse_json_response(response.text)
            
            updated_scope = scope.copy()
            activities = updated_scope.get('activities', [])
            changes = []
            
            if instruction['action'] == 'add':
                # Add new activity with validation
                new_activity = {
                    'name': instruction['activity_name'],
                    'description': instruction.get('activity_description', instruction['activity_name']),
                    'phase': instruction.get('target_phase', 'Development'),
                    'effort_days': max(1, instruction.get('effort_days', 5)),
                    'dependencies': instruction.get('dependencies', []),
                    'resources_needed': instruction.get('resources_required', ['Developer'])
                }
                activities.append(new_activity)
                changes = [f"Added: {new_activity['name']} ({new_activity['effort_days']} days in {new_activity['phase']})"]
                
            elif instruction['action'] == 'remove':
                # Remove matching activities
                original_count = len(activities)
                activities = [
                    a for a in activities 
                    if instruction['activity_name'].lower() not in a['name'].lower()
                ]
                removed_count = original_count - len(activities)
                if removed_count > 0:
                    changes = [f"Removed {removed_count} activity(ies) matching '{instruction['activity_name']}'"]
                else:
                    changes = [f"No activities found matching '{instruction['activity_name']}'"]
            
            else:  # modify
                # Modify existing activities
                modified_count = 0
                for activity in activities:
                    if instruction['activity_name'].lower() in activity['name'].lower():
                        activity.update({
                            'description': instruction.get('activity_description', activity.get('description')),
                            'phase': instruction.get('target_phase', activity.get('phase')),
                            'effort_days': instruction.get('effort_days', activity.get('effort_days'))
                        })
                        modified_count += 1
                
                changes = [f"Modified {modified_count} activity(ies)"]
            
            updated_scope['activities'] = activities
            
            # Recalculate timeline and resources
            updated_scope = self._recalculate_timeline(updated_scope)
            updated_scope = self._recalculate_resources(updated_scope)
            
            return {
                'updated_scope': updated_scope,
                'response': f"I've updated the activities. {changes[0]}",
                'changes_made': changes,
                'intent': RefinementIntent.MODIFY_TASKS
            }
            
        except Exception as e:
            print(f"Error in _modify_tasks: {e}")
            return {
                'updated_scope': scope,
                'response': "I couldn't modify the tasks. Please be more specific about what to add, remove, or change.",
                'changes_made': [],
                'intent': RefinementIntent.MODIFY_TASKS
            }
    
    async def _adjust_timeline(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced timeline adjustment with phase-level granularity"""
        
        message_lower = message.lower()
        
        # Extract specific duration changes
        weeks_match = re.search(r'(\d+)\s*weeks?', message_lower)
        months_match = re.search(r'(\d+)\s*months?', message_lower)
        
        if weeks_match:
            target_weeks = int(weeks_match.group(1))
            current_weeks = sum(p.get('duration_weeks', 0) for p in scope.get('timeline', {}).get('phases', []))
            adjustment_factor = target_weeks / current_weeks if current_weeks > 0 else 1.0
            direction = f"adjusted to {target_weeks} weeks"
        elif months_match:
            target_months = int(months_match.group(1))
            current_months = scope.get('timeline', {}).get('total_duration_months', 6)
            adjustment_factor = target_months / current_months if current_months > 0 else 1.0
            direction = f"adjusted to {target_months} months"
        elif any(word in message_lower for word in ['shorter', 'faster', 'quicker', 'reduce']):
            adjustment_factor = 0.85  # 15% shorter
            direction = "shortened by 15%"
        elif any(word in message_lower for word in ['longer', 'extend', 'increase']):
            adjustment_factor = 1.15  # 15% longer
            direction = "extended by 15%"
        else:
            adjustment_factor = 1.0
            direction = "unchanged"
        
        updated_scope = scope.copy()
        timeline = updated_scope.get('timeline', {})
        phases = timeline.get('phases', [])
        
        # Adjust phase durations with minimum constraints
        current_week = 1
        for phase in phases:
            original_duration = phase.get('duration_weeks', 4)
            new_duration = max(2, int(original_duration * adjustment_factor))  # Minimum 2 weeks per phase
            phase['duration_weeks'] = new_duration
            phase['start_week'] = current_week
            phase['end_week'] = current_week + new_duration - 1
            current_week += new_duration
        
        # Update total duration
        total_weeks = sum(p['duration_weeks'] for p in phases)
        timeline['total_duration_months'] = round(total_weeks / 4.33, 1)
        timeline['total_duration_weeks'] = total_weeks
        
        updated_scope['timeline'] = timeline
        
        # Recalculate resources based on new timeline
        updated_scope = self._recalculate_resources(updated_scope)
        
        changes = [
            f"Timeline {direction}",
            f"Total duration: {timeline['total_duration_months']} months ({total_weeks} weeks)",
            f"Phase durations adjusted proportionally"
        ]
        
        return {
            'updated_scope': updated_scope,
            'response': f"I've adjusted the timeline. New duration: {timeline['total_duration_months']} months.",
            'changes_made': changes,
            'intent': RefinementIntent.ADJUST_TIMELINE
        }
    
    async def _apply_discount(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced discount application with detailed breakdown"""
        
        # Extract discount percentage with better pattern matching
        discount_match = re.search(r'(\d+(?:\.\d+)?)\s*%', message)
        flat_match = re.search(r'\$(\d+(?:,\d+)*(?:\.\d+)?)', message)  # $ amount reduction
        
        updated_scope = scope.copy()
        resources = updated_scope.get('resources', [])
        cost_breakdown = updated_scope.get('cost_breakdown', {})
        
        original_total = cost_breakdown.get('total_cost', 0)
        changes = []
        
        if discount_match:
            discount_percent = float(discount_match.group(1))
            discount_factor = 1 - (discount_percent / 100)
            
            # Apply discount to all resources
            for resource in resources:
                original_cost = resource.get('total_cost', 0)
                resource['total_cost'] = round(original_cost * discount_factor, 2)
            
            changes.append(f"Applied {discount_percent}% discount")
            
        elif flat_match:
            discount_amount = float(flat_match.group(1).replace(',', ''))
            if discount_amount < original_total:
                discount_factor = 1 - (discount_amount / original_total)
                discount_percent = (1 - discount_factor) * 100
                
                for resource in resources:
                    original_cost = resource.get('total_cost', 0)
                    resource['total_cost'] = round(original_cost * discount_factor, 2)
                
                changes.append(f"Applied ${discount_amount:,.2f} discount ({discount_percent:.1f}%)")
            else:
                return {
                    'updated_scope': scope,
                    'response': f"Cannot apply ${discount_amount:,.2f} discount - it exceeds total cost of ${original_total:,.2f}",
                    'changes_made': ['Discount rejected - exceeds total cost'],
                    'intent': RefinementIntent.APPLY_DISCOUNT
                }
        else:
            # Default 10% discount
            discount_percent = 10
            discount_factor = 0.9
            
            for resource in resources:
                original_cost = resource.get('total_cost', 0)
                resource['total_cost'] = round(original_cost * discount_factor, 2)
            
            changes.append(f"Applied default {discount_percent}% discount")
        
        # Recalculate totals
        total_cost = sum(r.get('total_cost', 0) for r in resources)
        cost_breakdown['total_cost'] = total_cost
        cost_breakdown['discount_applied'] = discount_percent if 'discount_percent' in locals() else 0
        cost_breakdown['subtotal'] = original_total
        cost_breakdown['contingency_amount'] = round(
            total_cost * (cost_breakdown.get('contingency_percentage', 15) / 100),
            2
        )
        
        updated_scope['resources'] = resources
        updated_scope['cost_breakdown'] = cost_breakdown
        
        savings = original_total - total_cost
        changes.extend([
            f"New total cost: ${total_cost:,.2f}",
            f"Savings: ${savings:,.2f}"
        ])
        
        return {
            'updated_scope': updated_scope,
            'response': f"I've applied the discount. New total: ${total_cost:,.2f} (saved ${savings:,.2f})",
            'changes_made': changes,
            'intent': RefinementIntent.APPLY_DISCOUNT
        }
    
    async def _modify_resources(self, message: str, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced resource modification with role detection"""
        
        message_lower = message.lower()
        
        # Enhanced role detection
        role_keywords = {
            'frontend': 'Frontend Developer',
            'backend': 'Backend Developer', 
            'fullstack': 'Full Stack Developer',
            'designer': 'UI/UX Designer',
            'qa': 'QA Engineer',
            'tester': 'QA Engineer',
            'devops': 'DevOps Engineer',
            'pm': 'Project Manager',
            'manager': 'Project Manager',
            'analyst': 'Business Analyst',
            'architect': 'Solution Architect',
            'data': 'Data Engineer',
            'ml': 'ML Engineer',
            'security': 'Security Engineer'
        }
        
        detected_role = None
        for keyword, role_name in role_keywords.items():
            if keyword in message_lower:
                detected_role = role_name
                break
        
        if not detected_role:
            detected_role = 'Developer'  # Default
        
        # Detect count and action
        count_match = re.search(r'(\d+)', message)
        count_change = int(count_match.group(1)) if count_match else 1
        
        is_adding = any(word in message_lower for word in ['add', 'more', 'increase', 'additional'])
        is_removing = any(word in message_lower for word in ['remove', 'less', 'reduce', 'fewer'])
        
        # Default to adding if no clear action
        if not is_adding and not is_removing:
            is_adding = True
        
        updated_scope = scope.copy()
        resources = updated_scope.get('resources', [])
        
        # Find existing resource or create new
        existing_resource = next((r for r in resources if r['role'] == detected_role), None)
        
        changes = []
        
        if existing_resource:
            if is_adding:
                existing_resource['count'] += count_change
                changes.append(f"Added {count_change} {detected_role}(s)")
            elif is_removing:
                existing_resource['count'] = max(0, existing_resource['count'] - count_change)
                if existing_resource['count'] == 0:
                    resources = [r for r in resources if r['role'] != detected_role]
                    changes.append(f"Removed all {detected_role} positions")
                else:
                    changes.append(f"Removed {count_change} {detected_role}(s)")
            
            # Recalculate cost for existing resource
            if existing_resource in resources:
                existing_resource['total_cost'] = (
                    existing_resource['count'] * 
                    existing_resource['effort_months'] * 
                    existing_resource['monthly_rate']
                )
        else:
            if is_adding:
                # Add new resource with reasonable defaults
                new_resource = {
                    'role': detected_role,
                    'count': count_change,
                    'effort_months': updated_scope.get('timeline', {}).get('total_duration_months', 6),
                    'allocation_percentage': 100,
                    'monthly_rate': self._get_default_rate(detected_role),
                    'total_cost': count_change * updated_scope.get('timeline', {}).get('total_duration_months', 6) * self._get_default_rate(detected_role)
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
            'response': f"I've updated the team composition. {changes[0]}. New total: ${total_cost:,.2f}",
            'changes_made': changes,
            'intent': RefinementIntent.MODIFY_RESOURCES
        }
    
    async def _generic_refinement(self, message: str, scope: Dict[str, Any], intent: RefinementIntent) -> Dict[str, Any]:
        """Enhanced generic refinement with better suggestions"""
        
        prompt = f"""
User wants to refine the project scope. Provide helpful, specific guidance.

User Request: "{message}"

Current Scope Summary:
- Total Duration: {scope.get('timeline', {}).get('total_duration_months', 0)} months
- Total Cost: ${scope.get('cost_breakdown', {}).get('total_cost', 0):,.2f}
- Team Size: {len(scope.get('resources', []))} roles
- Activities: {len(scope.get('activities', []))} tasks

Based on their request, suggest specific, actionable refinements they can make.
Be concise but helpful.

Return ONLY plain text response.
"""
        
        try:
            response = self.model.generate_content(prompt)
            
            return {
                'updated_scope': scope,
                'response': response.text.strip(),
                'changes_made': ['No automatic changes made - provided guidance only'],
                'intent': intent
            }
            
        except Exception as e:
            return {
                'updated_scope': scope,
                'response': "I understand you'd like to refine the scope. Here are some specific changes you can request:\n• 'Make timeline 2 weeks shorter/longer'\n• 'Add security testing activities' \n• 'Apply 10% discount or $5000 off'\n• 'Add 2 more frontend developers'\n• 'Remove manual testing phase'",
                'changes_made': [],
                'intent': intent
            }
    
    def _recalculate_timeline(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced timeline recalculation with parallel work estimation"""
        activities = scope.get('activities', [])
        total_effort_days = sum(a.get('effort_days', 0) for a in activities)
        
        # Enhanced estimation considering parallel work streams
        # Assume 3-5 parallel streams based on project size
        parallel_streams = min(5, max(3, len(activities) // 10))
        estimated_weeks = max(4, int(total_effort_days / 5 / parallel_streams))
        
        timeline = scope.get('timeline', {})
        timeline['total_duration_months'] = round(estimated_weeks / 4.33, 1)
        timeline['total_duration_weeks'] = estimated_weeks
        
        # Update phase durations proportionally
        phases = timeline.get('phases', [])
        if phases:
            total_phase_weeks = sum(p.get('duration_weeks', 0) for p in phases)
            if total_phase_weeks > 0:
                scale_factor = estimated_weeks / total_phase_weeks
                current_week = 1
                for phase in phases:
                    new_duration = max(2, int(phase.get('duration_weeks', 4) * scale_factor))
                    phase['duration_weeks'] = new_duration
                    phase['start_week'] = current_week
                    phase['end_week'] = current_week + new_duration - 1
                    current_week += new_duration
        
        scope['timeline'] = timeline
        return scope
    
    def _recalculate_resources(self, scope: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced resource recalculation with timeline alignment"""
        timeline = scope.get('timeline', {})
        total_months = timeline.get('total_duration_months', 6)
        
        resources = scope.get('resources', [])
        for resource in resources:
            # Adjust effort_months based on new timeline, but respect role constraints
            # PMs typically work full duration, developers might phase in/out
            if resource['role'] in ['Project Manager', 'Business Analyst']:
                resource['effort_months'] = total_months
            else:
                # Technical roles might have staggered allocation
                resource['effort_months'] = min(
                    total_months,
                    resource.get('effort_months', total_months * 0.8)  # Default to 80% of timeline
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
    
    def _get_default_rate(self, role: str) -> float:
        """Get default monthly rate for a role"""
        rates = {
            'Project Manager': 10000,
            'Business Analyst': 8000,
            'UI/UX Designer': 7000,
            'Frontend Developer': 8000,
            'Backend Developer': 8500,
            'Full Stack Developer': 9000,
            'QA Engineer': 7000,
            'DevOps Engineer': 9000,
            'Solution Architect': 12000,
            'Data Engineer': 9500,
            'ML Engineer': 11000,
            'Security Engineer': 10000,
            'Developer': 8000
        }
        return rates.get(role, 8000)
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Enhanced JSON parsing with better error handling"""
        try:
            # Remove markdown code blocks and clean
            text = re.sub(r'```json\s*', '', response_text)
            text = re.sub(r'```\s*', '', text).strip()
            
            # Find JSON object with multiple attempts
            json_pattern = r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}'
            matches = re.finditer(json_pattern, text, re.DOTALL)
            
            for match in matches:
                try:
                    json_str = match.group()
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
            
            # If no valid JSON found, try parsing as simple structure
            raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"JSON parsing error: {e}")
            # Return safe default
            return {
                "action": "add",
                "activity_name": "Additional task",
                "target_phase": "Development", 
                "effort_days": 5,
                "dependencies": [],
                "resources_required": ["Developer"]
            }


# Global instance
refinement_engine = RefinementEngine()