import React, { useState, useEffect } from "react";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Enhanced Progress Page with Interactive Checklist and Full Noir Theme
const ProgressPage = () => {
  const [progressItems, setProgressItems] = useState([]);
  const [editingNotes, setEditingNotes] = useState(null);
  const [tempNote, setTempNote] = useState('');
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchProgressItems();
  }, []);

  const fetchProgressItems = async () => {
    try {
      const response = await axios.get(`${API}/api/progress/items`);
      setProgressItems(response.data.items || []);
    } catch (error) {
      console.error('Error fetching progress items:', error);
      // Enhanced fallback data with noir theming
      setProgressItems([
        {
          id: '1',
          title: 'Gather Birth Certificate',
          description: 'Obtain certified copy of birth certificate for visa application',
          status: 'completed',
          category: 'Documentation',
          priority: 'high',
          code: 'DOC-001',
          subtasks: [
            { task: 'Request birth certificate online', completed: true },
            { task: 'Pay processing fee', completed: true },
            { task: 'Receive by mail', completed: true }
          ],
          notes: 'Received certified copy from state office. Cost $25. Expedited processing completed successfully.'
        },
        {
          id: '2',
          title: 'Complete Visa Application Form',
          description: 'Fill out UK Skilled Worker visa application online',
          status: 'in_progress',
          category: 'Visa Application',
          priority: 'urgent',
          code: 'VIS-002',
          subtasks: [
            { task: 'Create UK government account', completed: true },
            { task: 'Fill application form sections 1-3', completed: true },
            { task: 'Upload supporting documents', completed: false },
            { task: 'Submit final application', completed: false }
          ],
          notes: 'Application 75% complete. Awaiting document uploads.'
        },
        {
          id: '3',
          title: 'Research Peak District Employment',
          description: 'Identify and analyze job opportunities in target region',
          status: 'completed',
          category: 'Employment',
          priority: 'medium',
          code: 'EMP-003',
          subtasks: [
            { task: 'Compile job board listings', completed: true },
            { task: 'Network with local professionals', completed: true },
            { task: 'Create target company list', completed: true }
          ],
          notes: 'Identified 12 potential opportunities. 3 companies showing strong interest.'
        }
      ]);
    }
  };

  const updateItemStatus = async (itemId, newStatus) => {
    try {
      await axios.put(`${API}/api/progress/items/${itemId}`, {
        status: newStatus
      });
      fetchProgressItems();
    } catch (error) {
      console.error('Error updating item status:', error);
      // Update local state for demo
      setProgressItems(prev => prev.map(item => 
        item.id === itemId ? { ...item, status: newStatus } : item
      ));
    }
  };

  const toggleSubtask = async (itemId, subtaskIndex) => {
    try {
      await axios.post(`${API}/api/progress/items/${itemId}/subtasks/${subtaskIndex}/toggle`);
      fetchProgressItems();
    } catch (error) {
      console.error('Error toggling subtask:', error);
      // Update local state for demo
      setProgressItems(prev => prev.map(item => {
        if (item.id === itemId) {
          const newSubtasks = [...item.subtasks];
          newSubtasks[subtaskIndex] = {
            ...newSubtasks[subtaskIndex],
            completed: !newSubtasks[subtaskIndex].completed
          };
          return { ...item, subtasks: newSubtasks };
        }
        return item;
      }));
    }
  };

  const saveNotes = async (itemId, notes) => {
    try {
      await axios.put(`${API}/api/progress/items/${itemId}`, {
        notes: notes
      });
      setEditingNotes(null);
      setTempNote('');
      fetchProgressItems();
    } catch (error) {
      console.error('Error saving notes:', error);
      // Update local state for demo
      setProgressItems(prev => prev.map(item => 
        item.id === itemId ? { ...item, notes: notes } : item
      ));
      setEditingNotes(null);
      setTempNote('');
    }
  };

  const startEditingNotes = (item) => {
    setEditingNotes(item.id);
    setTempNote(item.notes || '');
  };

  const getStatusConfig = (status) => {
    switch (status) {
      case 'completed': 
        return { 
          color: 'border-noir-white text-noir-white bg-noir-charcoal',
          icon: '✅',
          label: 'COMPLETED',
          glow: 'glow-text'
        };
      case 'in_progress': 
        return { 
          color: 'border-noir-accent text-noir-accent bg-noir-deep-red',
          icon: '🔄',
          label: 'IN PROGRESS',
          glow: 'glow-red'
        };
      case 'blocked': 
        return { 
          color: 'border-red-600 text-red-400 bg-red-900',
          icon: '🚫',
          label: 'BLOCKED',
          glow: 'glow-red'
        };
      default: 
        return { 
          color: 'border-noir-grey text-noir-grey bg-noir-black',
          icon: '⏳',
          label: 'NOT STARTED',
          glow: ''
        };
    }
  };

  const getPriorityConfig = (priority) => {
    switch (priority) {
      case 'urgent':
        return { color: 'text-noir-accent glow-red', badge: 'PRIORITY ALPHA' };
      case 'high':
        return { color: 'text-orange-400', badge: 'HIGH PRIORITY' };
      case 'medium':
        return { color: 'text-noir-grey', badge: 'STANDARD' };
      default:
        return { color: 'text-noir-grey', badge: 'LOW PRIORITY' };
    }
  };

  const filteredItems = progressItems.filter(item => {
    if (filterCategory !== 'all' && item.category !== filterCategory) return false;
    if (filterStatus !== 'all' && item.status !== filterStatus) return false;
    return true;
  });

  const completedItems = progressItems.filter(item => item.status === 'completed').length;
  const totalItems = progressItems.length;

  const categories = [...new Set(progressItems.map(item => item.category))];
  const statuses = ['not_started', 'in_progress', 'completed', 'blocked'];

  return (
    <div className="min-h-screen bg-noir-gradient p-6">
      <div className="max-w-7xl mx-auto">
        {/* Cinematic Header */}
        <div className="text-center mb-12 fade-in">
          <h1 className="noir-display text-5xl md:text-7xl mb-8 glow-text typewriter">
            STATUS TRACKING
          </h1>
          <p className="noir-mono text-xl md:text-2xl text-noir-grey mb-8 tracking-wide">
            [ INTERACTIVE MISSION PROGRESS MONITOR ]
          </p>
          
          {/* Enhanced Progress Overview */}
          <div className="card-noir p-8 mb-12">
            <h2 className="noir-title text-3xl mb-6 glow-text">MISSION PROGRESS</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="card-noir p-6 text-center scale-in">
                <div className="noir-display text-4xl mb-3 glow-text">{totalItems}</div>
                <div className="noir-mono text-sm text-noir-grey tracking-wider">TOTAL ITEMS</div>
              </div>
              <div className="card-noir p-6 text-center scale-in" style={{animationDelay: '0.1s'}}>
                <div className="noir-display text-4xl mb-3 text-noir-accent glow-red">{completedItems}</div>
                <div className="noir-mono text-sm text-noir-grey tracking-wider">COMPLETED</div>
              </div>
              <div className="card-noir p-6 text-center scale-in" style={{animationDelay: '0.2s'}}>
                <div className="noir-display text-4xl mb-3 glow-text">{totalItems - completedItems}</div>
                <div className="noir-mono text-sm text-noir-grey tracking-wider">REMAINING</div>
              </div>
              <div className="card-noir p-6 text-center scale-in" style={{animationDelay: '0.3s'}}>
                <div className="noir-display text-4xl mb-3 glow-text">
                  {totalItems > 0 ? Math.round((completedItems / totalItems) * 100) : 0}%
                </div>
                <div className="noir-mono text-sm text-noir-grey tracking-wider">COMPLETE</div>
              </div>
            </div>
            
            <div className="progress-noir">
              <div 
                className="progress-noir-fill"
                style={{ width: `${totalItems > 0 ? (completedItems / totalItems) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Enhanced Filters */}
        <div className="card-noir p-6 mb-12 slide-in-left">
          <h2 className="noir-title text-2xl mb-6">FILTER CONTROLS</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block noir-mono text-sm text-noir-grey mb-3 tracking-wider">CATEGORY</label>
              <select
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
                className="select-noir w-full"
              >
                <option value="all">ALL CATEGORIES</option>
                {categories.map(category => (
                  <option key={category} value={category}>{category.toUpperCase()}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block noir-mono text-sm text-noir-grey mb-3 tracking-wider">STATUS</label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="select-noir w-full"
              >
                <option value="all">ALL STATUSES</option>
                {statuses.map(status => (
                  <option key={status} value={status}>{status.replace('_', ' ').toUpperCase()}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={() => {
                  setFilterCategory('all');
                  setFilterStatus('all');
                }}
                className="btn-noir w-full"
              >
                [RESET] CLEAR FILTERS
              </button>
            </div>
          </div>
          
          <div className="mt-6 text-center">
            <span className="noir-mono text-noir-grey">
              Showing {filteredItems.length} of {totalItems} items
            </span>
          </div>
        </div>

        {/* Enhanced Progress Items */}
        <div className="space-y-8">
          {filteredItems.map((item, index) => {
            const statusConfig = getStatusConfig(item.status);
            const priorityConfig = getPriorityConfig(item.priority);
            const completedSubtasks = item.subtasks.filter(st => st.completed).length;
            const totalSubtasks = item.subtasks.length;
            
            return (
              <div 
                key={item.id} 
                className="card-noir p-8 hover:scale-102 transition-all duration-700 scale-in"
                style={{animationDelay: `${index * 0.1}s`}}
              >
                {/* Header with enhanced styling */}
                <div className="flex items-start justify-between mb-8">
                  <div className="flex items-center space-x-8">
                    <div className={`w-20 h-20 border-2 flex items-center justify-center text-3xl font-bold transition-all duration-500 ${statusConfig.color} ${statusConfig.glow}`}>
                      {statusConfig.icon}
                    </div>
                    <div>
                      <div className="flex items-center space-x-4 mb-3">
                        <h2 className="noir-title text-2xl md:text-3xl tracking-wide">{item.title}</h2>
                        <span className="noir-mono text-xs text-noir-accent">{item.code}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <span className={`btn-noir text-xs px-4 py-2 ${statusConfig.color} ${statusConfig.glow}`}>
                          {statusConfig.label}
                        </span>
                        <span className={`noir-mono text-sm ${priorityConfig.color}`}>
                          {priorityConfig.badge}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <select
                      value={item.status}
                      onChange={(e) => updateItemStatus(item.id, e.target.value)}
                      className="select-noir"
                    >
                      <option value="not_started">NOT STARTED</option>
                      <option value="in_progress">IN PROGRESS</option>
                      <option value="completed">COMPLETED</option>
                      <option value="blocked">BLOCKED</option>
                    </select>
                  </div>
                </div>

                <p className="noir-serif text-lg text-noir-grey mb-8 leading-relaxed">{item.description}</p>

                {/* Enhanced Progress Bar */}
                <div className="mb-8">
                  <div className="flex justify-between items-center mb-4">
                    <span className="noir-mono text-sm text-noir-grey tracking-wider uppercase">SUBTASK PROGRESS</span>
                    <span className="noir-mono text-sm text-noir-grey">
                      {completedSubtasks}/{totalSubtasks} COMPLETE
                    </span>
                  </div>
                  <div className="progress-noir">
                    <div 
                      className="progress-noir-fill"
                      style={{ width: `${totalSubtasks > 0 ? (completedSubtasks / totalSubtasks) * 100 : 0}%` }}
                    ></div>
                  </div>
                </div>

                {/* Enhanced Interactive Subtasks */}
                <div className="space-y-4 mb-8">
                  <h3 className="noir-title text-lg text-shadow-noir">TASK CHECKLIST:</h3>
                  {item.subtasks.map((subtask, subIndex) => (
                    <label key={subIndex} className="flex items-center cursor-pointer group">
                      <input
                        type="checkbox"
                        checked={subtask.completed}
                        onChange={() => toggleSubtask(item.id, subIndex)}
                        className="checkbox-noir mr-4"
                      />
                      <span className={`noir-serif text-lg transition-all duration-300 group-hover:text-noir-white ${
                        subtask.completed ? 'line-through text-noir-grey' : 'text-noir-off-white'
                      }`}>
                        {subtask.task}
                      </span>
                      {subtask.completed && (
                        <span className="ml-4 text-noir-accent glow-red">✅</span>
                      )}
                    </label>
                  ))}
                </div>

                {/* Enhanced Notes Section */}
                <div className="border-t border-noir-grey pt-8">
                  <h3 className="noir-title text-lg mb-6 text-shadow-noir">OPERATIONAL NOTES:</h3>
                  {editingNotes === item.id ? (
                    <div className="space-y-6">
                      <textarea
                        value={tempNote}
                        onChange={(e) => setTempNote(e.target.value)}
                        className="input-noir w-full h-32 resize-none"
                        placeholder="Enter operational intelligence..."
                      />
                      <div className="flex space-x-4">
                        <button
                          onClick={() => saveNotes(item.id, tempNote)}
                          className="btn-noir btn-noir-primary"
                        >
                          [SAVE] UPDATE NOTES
                        </button>
                        <button
                          onClick={() => {
                            setEditingNotes(null);
                            setTempNote('');
                          }}
                          className="btn-noir"
                        >
                          [CANCEL] ABORT
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="card-noir p-6 bg-noir-charcoal">
                        <p className="noir-serif text-lg text-noir-off-white leading-relaxed">
                          {item.notes || 'No operational intelligence recorded. Click "EDIT NOTES" to add classified data.'}
                        </p>
                      </div>
                      <button
                        onClick={() => startEditingNotes(item)}
                        className="link-noir noir-mono font-bold tracking-wider hover:glow-text"
                      >
                        [EDIT NOTES] MODIFY INTELLIGENCE
                      </button>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {filteredItems.length === 0 && (
          <div className="text-center py-16">
            <div className="card-noir p-12">
              <div className="text-8xl mb-8">📋</div>
              <h2 className="noir-display text-4xl mb-6 glow-text">NO ACTIVE MISSIONS</h2>
              <p className="noir-serif text-lg text-noir-grey mb-8">
                Initialize timeline sequence to generate progress items.
              </p>
              <button
                onClick={() => {
                  setFilterCategory('all');
                  setFilterStatus('all');
                }}
                className="btn-noir btn-noir-primary"
              >
                [RESET] SHOW ALL ITEMS
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressPage;