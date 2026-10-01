import React, { useState } from 'react';
import { 
  Youtube, 
  Facebook, 
  Instagram, 
  Bot, 
  Cloud, 
  Zap, 
  ShieldCheck, 
  Layers, 
  Sparkles,
  ChevronDown,
  ArrowRight,
  Music,
  CheckCircle2,
  HelpCircle,
  Film
} from 'lucide-react';
import { PlatformConfig, PLATFORMS_MAP } from '../config/platforms';

interface FeaturesSectionProps {
  platform: PlatformConfig;
  onSelectPlatform: (slug: string) => void;
}

const ALL_PLATFORMS_LIST = [
  PLATFORMS_MAP.youtube,
  PLATFORMS_MAP.instagram,
  PLATFORMS_MAP.facebook,
  PLATFORMS_MAP.tiktok,
  PLATFORMS_MAP.twitter,
  PLATFORMS_MAP.reddit
];

export const FeaturesSection: React.FC<FeaturesSectionProps> = ({ 
  platform, 
  onSelectPlatform 
}) => {
  const [openFaqIndex, setOpenFaqIndex] = useState<number | null>(0);

  const toggleFaq = (idx: number) => {
    setOpenFaqIndex(openFaqIndex === idx ? null : idx);
  };

  return (
    <div className="w-full max-w-5xl mx-auto space-y-16 py-6 sm:py-10">
      {/* 1. Platform-Specific Core Value Props / Features */}
      <section className="space-y-6">
        <div className="text-center space-y-1.5">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-100">
            {platform.shortName} Features
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-display">
            Why Use Our {platform.name}?
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
            Engineered for high resolution, maximum bandwidth, and strict user privacy.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {platform.features.map((feat, idx) => {
            const FeatIcon = feat.icon;
            return (
              <div
                key={idx}
                className="card-clean rounded-2xl p-5 border border-slate-200/80 space-y-3 bg-white hover:border-slate-300 transition-all hover:shadow-xs"
              >
                <div className="w-10 h-10 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-800">
                  <FeatIcon className="w-5 h-5 text-blue-600 stroke-[2.2]" />
                </div>
                <h3 className="text-sm font-bold text-slate-900 font-display">
                  {feat.title}
                </h3>
                <p className="text-xs text-slate-500 leading-relaxed">
                  {feat.desc}
                </p>
              </div>
            );
          })}
        </div>
      </section>

      {/* 2. Step-by-Step "How to Download" Guide (SEO Optimized) */}
      <section id="how-to-use" className="card-clean rounded-3xl p-6 sm:p-10 space-y-8 bg-white border border-slate-200/80 shadow-soft">
        <div className="text-center space-y-1.5">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">
            Quick Tutorial
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-display">
            How to Download from {platform.shortName}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 max-w-lg mx-auto">
            Save any video or media stream in 3 quick steps without installing software.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
          {platform.howToSteps.map((step, idx) => (
            <div
              key={idx}
              className="bg-slate-50/70 rounded-2xl p-6 border border-slate-200/60 text-center space-y-3 relative group hover:bg-slate-50 transition-colors"
            >
              <div className="w-10 h-10 rounded-full bg-slate-900 text-white font-bold text-sm flex items-center justify-center mx-auto shadow-xs">
                {step.step}
              </div>
              <h3 className="text-base font-bold text-slate-900 font-display">
                {step.title}
              </h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                {step.desc}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* 3. Platform SEO Frequently Asked Questions (FAQ Accordion) */}
      <section id="faqs" className="space-y-6 max-w-3xl mx-auto">
        <div className="text-center space-y-1.5">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-600 bg-slate-100 px-3 py-1 rounded-full">
            Help & Information
          </span>
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-display">
            Frequently Asked Questions
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Everything you need to know about downloading {platform.shortName} media with DownFromNet.
          </p>
        </div>

        <div className="space-y-3">
          {platform.faqs.map((faq, idx) => {
            const isOpen = openFaqIndex === idx;
            return (
              <div
                key={idx}
                className="card-clean rounded-2xl border border-slate-200/80 bg-white overflow-hidden transition-colors"
              >
                <button
                  type="button"
                  onClick={() => toggleFaq(idx)}
                  className="w-full flex items-center justify-between p-5 text-left font-bold text-slate-900 text-sm sm:text-base hover:text-blue-600 transition-colors cursor-pointer"
                  aria-expanded={isOpen}
                >
                  <span className="flex items-center gap-2.5 pr-4">
                    <HelpCircle className="w-4 h-4 text-slate-400 shrink-0" />
                    <span>{faq.question}</span>
                  </span>
                  <ChevronDown className={`w-4 h-4 text-slate-400 shrink-0 transition-transform duration-200 ${isOpen ? 'rotate-180 text-blue-600' : ''}`} />
                </button>

                {isOpen && (
                  <div className="px-5 pb-5 pt-1 text-xs sm:text-sm text-slate-600 leading-relaxed border-t border-slate-100/80 bg-slate-50/40 animate-in fade-in duration-150">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>

      {/* 4. Cross-Platform Exploration Hub (SEO Internal Linking) */}
      <section id="platforms" className="space-y-6">
        <div className="text-center space-y-1.5">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 font-display">
            Explore Other Supported Platforms
          </h2>
          <p className="text-sm text-slate-500 max-w-lg mx-auto">
            Switch between dedicated downloaders for YouTube, Instagram, Facebook, TikTok, Twitter/X, and Reddit.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {ALL_PLATFORMS_LIST.map((item, idx) => {
            const ItemIcon = item.icon;
            const isCurrent = item.id === platform.id;
            return (
              <div
                key={idx}
                onClick={() => onSelectPlatform(item.slug)}
                className={`group card-clean rounded-2xl p-5 border-t-[3px] ${item.borderColor} flex flex-col justify-between space-y-4 cursor-pointer transition-all hover:border-slate-300 hover:shadow-xs bg-white ${
                  isCurrent ? 'ring-2 ring-slate-900/10' : ''
                }`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className={`w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center ${item.iconColor} group-hover:scale-105 transition-transform`}>
                      <ItemIcon className="w-5 h-5" />
                    </div>
                    <span className="text-[11px] font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                      {isCurrent ? 'Current Page' : 'Free Tool'}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-base font-bold text-slate-900 font-display">
                      {item.name}
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 leading-relaxed line-clamp-2">
                      {item.subtitle}
                    </p>
                  </div>
                </div>

                <div className="pt-2 flex items-center gap-1 text-xs font-semibold text-slate-700 group-hover:text-blue-600 transition-colors">
                  <span>Open {item.shortName} Downloader</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
};
