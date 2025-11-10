//frontend/src/components/RefinementBar.jsx
import React, { useState } from 'react';
import { MessageCircle, Zap, Clock, DollarSign, Users, History } from 'lucide-react';

const RefinementBar = ({ onRefine, loading, refinements, currentStep, onStepChange }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !loading) {
      onRefine(message);
      setMessage('');
    }
  };

  const quickActions = [
    {
      icon: Clock,
      label: 'Shorter timeline',
      message: 'Make the timeline 2 weeks shorter'
    },
    {
      icon: DollarSign,
      label: '10% discount',
      message: 'Apply 10% discount to total cost'
    },
    {
      icon: Users,
      label: 'Add developer',
      message: 'Add 1 more frontend developer'
    },
    {
      icon: Zap,
      label: 'Add security',
      message: 'Add security testing activities'
    }
  ];

  const getIntentIcon = (intent) => {
    switch (intent) {
      case 'modify_tasks': return Zap;
      case 'adjust_timeline': return Clock;
      case 'apply_discount': return DollarSign;
      case 'modify_resources': return Users;
      default: return MessageCircle;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 sticky top-6">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <MessageCircle className="text-blue-500" />
        Real-time Refinement
      </h2>

      {/* Quick Actions */}
      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">Quick Actions:</p>
        <div className="grid grid-cols-2 gap-2">
          {quickActions.map((action, idx) => {
            const Icon = action.icon;
            return (
              <button
                key={idx}
                onClick={() => setMessage(action.message)}
                className="flex items-center gap-1 p-2 text-xs bg-gray-100 hover:bg-gray-200 rounded transition-colors"
              >
                <Icon size={14} />
                <span className="truncate">{action.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Refinement History */}
      {refinements.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <History size={16} />
            Refinement History ({refinements.length})
          </div>
          <div className="max-h-32 overflow-y-auto space-y-2">
            {refinements.slice(-3).reverse().map((refinement) => {
              const IntentIcon = getIntentIcon(refinement.intent);
              return (
                <div key={refinement.id} className="text-xs bg-gray-50 p-2 rounded">
                  <div className="flex items-center gap-1 mb-1">
                    <IntentIcon size={12} />
                    <span className="font-medium capitalize">{refinement.intent.replace('_', ' ')}</span>
                  </div>
                  <p className="text-gray-600 truncate">{refinement.changes[0]}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Chat Input */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me to refine the scope... (e.g., 'Add security testing', 'Make it 10% cheaper', 'Extend timeline by 2 weeks')"
            className="w-full border border-gray-300 rounded px-3 py-2 text-sm resize-none h-20"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !message.trim()}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded font-medium disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              Processing...
            </>
          ) : (
            <>
              <Zap size={16} />
              Refine Scope
            </>
          )}
        </button>
      </form>

      {/* Step Navigation */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex gap-2">
          {currentStep > 3 && (
            <button
              onClick={() => onStepChange(4)}
              className="flex-1 bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded text-sm"
            >
              Back to Refine
            </button>
          )}
          {currentStep === 4 && (
            <button
              onClick={() => onStepChange(5)}
              className="flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded text-sm font-medium"
            >
              Finalize Scope
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default RefinementBar;