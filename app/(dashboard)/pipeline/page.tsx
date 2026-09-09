import { useState, useEffect } from 'react';
import { formatDate } from '../../lib/types';

export default function PipelinePage() {
  const [pipeline_stages, setPipelineStages] = useState({
    discovery: 'Discovery',
    normalization: 'Normalisation',
    deduplication: 'Deduplication',
    enrichment: 'Enrichment',
    verification: 'Verification',
    scoring: 'Scoring',
    approval: 'Approval',
    outreach: 'Outreach',
  });
  const [stage, setStage] = useState(pipeline_stages.discovery);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    // Simulate pipeline progression
    const interval = setInterval(() => {
      setProgress(prev => Math.min(prev + 5, 100));
      if (progress >= 100) {
        setStage('completed');
        setProgress(100);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [progress]);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-4">Pipeline</h1>
      <p className="text-gray-600 mb-6">Track your lead intelligence pipeline through each stage</p>
      
      <div className="flex items-center gap-2 mb-6">
        <span className="text-2xl font-bold">{progress}%</span>
        <select 
          value={stage} 
          onChange={(e) => setStage(e.target.value)}
          className="border border-gray-300 rounded px-3 py-1 outline-none"
        >
          <option value="discovery">Discovery</option>
          <option value="normalisation">Normalisation</option>
          <option value="deduplication">Deduplication</option>
          <option value="enrichment">Enrichment</option>
          <option value="verification">Verification</option>
          <option value="scoring">Scoring</option>
          <option value="approval">Approval</option>
          <option value="outreach">Outreach</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div className="space-y-4">
        {Object.entries(pipeline_stages).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between py-3 border-b border-gray-100">
            <span className="text-gray-600">{key}: {value}</span>
            <span className="text-sm text-gray-500">{progress}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
