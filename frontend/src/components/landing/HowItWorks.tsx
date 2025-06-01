'use client';

import { motion } from "framer-motion";
import { Upload, Languages, BookOpen, Download } from "lucide-react";

const steps = [
  {
    name: "Upload Your Comic",
    description: "Upload your comic or manga in PDF format. We support most common comic formats.",
    icon: Upload,
  },
  {
    name: "Choose Language",
    description: "Select your target language from our extensive list of supported languages.",
    icon: Languages,
  },
  {
    name: "Read Instantly",
    description: "Start reading your translated comic immediately as pages are processed.",
    icon: BookOpen,
  },
  {
    name: "Download & Share",
    description: "Download your translated comic or share it directly with friends.",
    icon: Download,
  },
];

export function HowItWorks() {
  return (
    <div id="how-it-works" className="bg-background py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-primary">Simple Process</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            How It Works
          </p>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Translate your comics in just a few simple steps. Our AI handles the complex parts while you enjoy the results.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <div className="grid grid-cols-1 gap-y-8 gap-x-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step, index) => (
              <motion.div
                key={step.name}
                className="relative pl-9"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <div className="absolute left-0 top-0 flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
                  <step.icon className="h-5 w-5 text-primary" aria-hidden="true" />
                </div>
                <h3 className="text-lg font-semibold leading-8 text-foreground">
                  {step.name}
                </h3>
                <p className="mt-2 text-base leading-7 text-muted-foreground">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 