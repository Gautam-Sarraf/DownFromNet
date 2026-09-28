import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';

export const LegalNotice: React.FC = () => {
  return (
    <div className="w-full max-w-4xl mx-auto p-4 rounded-2xl bg-white border border-slate-200/90 text-xs text-slate-500 space-y-1.5 shadow-2xs">
      <div className="flex items-center gap-2 text-slate-700 font-semibold">
        <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
        <span>Usage Notice & Legal Compliance</span>
      </div>
      <p className="leading-relaxed">
        Only download publicly accessible media content that you have explicit authorization or legal permission to download. DownFromNet respects copyright, intellectual property rights, and platform terms of service, and does not circumvent access controls, DRM, or paywalls.
      </p>
    </div>
  );
};
