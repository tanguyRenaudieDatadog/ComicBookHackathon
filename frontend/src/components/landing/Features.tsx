'use client';

import { motion } from "framer-motion";
import { BookOpen, Globe, Zap, Shield } from "lucide-react";

const features = [
  {
    name: "Multi-language Support",
    description: "Translate comics into any language while preserving the original art and style.",
    icon: Globe,
  },
  {
    name: "Instant Translation",
    description: "Get your translated comics in minutes with our advanced AI technology.",
    icon: Zap,
  },
  {
    name: "Digital Library",
    description: "Build your personal collection of translated comics with our built-in reader.",
    icon: BookOpen,
  },
  {
    name: "Secure & Private",
    description: "Your comics are processed securely and never shared with third parties.",
    icon: Shield,
  },
];

export function Features() {
  return (
    <div id="features" className="bg-background py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl lg:text-center">
          <h2 className="text-base font-semibold leading-7 text-primary">Faster Translation</h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Everything you need to translate your comics
          </p>
          <p className="mt-6 text-lg leading-8 text-muted-foreground">
            Our platform combines cutting-edge AI technology with a user-friendly interface to make comic translation accessible to everyone.
          </p>
        </div>
        <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
          <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.name}
                className="flex flex-col"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <dt className="flex items-center gap-x-3 text-base font-semibold leading-7 text-foreground">
                  <feature.icon className="h-5 w-5 flex-none text-primary" aria-hidden="true" />
                  {feature.name}
                </dt>
                <dd className="mt-4 flex flex-auto flex-col text-base leading-7 text-muted-foreground">
                  <p className="flex-auto">{feature.description}</p>
                </dd>
              </motion.div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
} 