import { Brain, Database, Cpu, GitBranch, FlaskConical, Award } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Deep Learning Core",
    description:
      "SmogNet v3 uses a temporal convolutional network (TCN) trained on 10+ years of satellite imagery and ground sensor data to predict air quality 72 hours ahead.",
  },
  {
    icon: Database,
    title: "Multi-Source Data Fusion",
    description:
      "Integrates Sentinel-5P satellite, OpenAQ ground stations, meteorological APIs, and traffic density data for comprehensive input features.",
  },
  {
    icon: Cpu,
    title: "Edge-Optimized Inference",
    description:
      "Quantized model runs in under 50ms per prediction on commodity hardware, enabling real-time alerts without cloud latency.",
  },
  {
    icon: GitBranch,
    title: "Ensemble Architecture",
    description:
      "Combines three specialized sub-models (PM2.5, NO₂, O₃) with a meta-learner that weights predictions based on local meteorological conditions.",
  },
  {
    icon: FlaskConical,
    title: "Continuous Retraining",
    description:
      "Active learning pipeline automatically flags high-error predictions and queues them for model updates, keeping accuracy above 90% year-round.",
  },
  {
    icon: Award,
    title: "Validated Performance",
    description:
      "Independently validated against WHO air quality guidelines. Mean Absolute Error (MAE) of 8.4 AQI units on a held-out test set from 2023–2025.",
  },
];

const timeline = [
  { year: "2021", event: "Research started, initial dataset collected from 3 cities" },
  { year: "2022", event: "SmogNet v1 released, covering PM2.5 predictions" },
  { year: "2023", event: "v2 introduced multi-pollutant forecasting and satellite fusion" },
  { year: "2024", event: "v3 added 72-hour ensemble forecasting across Central Asia" },
  { year: "2025", event: "Edge deployment and open-data API launched" },
  { year: "2026", event: "Current: real-time dashboard with 6 monitored cities" },
];

export default function AboutPage() {
  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="max-w-3xl">
        <h1 className="text-3xl font-bold text-env-text-primary">
          About the Model
        </h1>
        <p className="mt-3 text-env-text-secondary leading-relaxed">
          SmogNet is an open-source deep learning system for real-time smog and
          air quality prediction. It was developed to provide accurate,
          interpretable air quality forecasts for cities across Central Asia
          where monitoring infrastructure is limited.
        </p>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-3">
        {features.map(({ icon: Icon, title, description }) => (
          <div
            key={title}
            className="rounded-xl border border-env-border bg-env-card p-5 hover:border-env-green-500/50 transition-colors"
          >
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-env-surface border border-env-border">
              <Icon size={20} className="text-env-green-400" />
            </div>
            <h3 className="mb-2 font-semibold text-env-text-primary">{title}</h3>
            <p className="text-sm text-env-text-secondary leading-relaxed">
              {description}
            </p>
          </div>
        ))}
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "MAE (AQI)", value: "8.4" },
          { label: "24h Accuracy", value: "94.2%" },
          { label: "Cities Covered", value: "6" },
          { label: "Training Years", value: "10+" },
        ].map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-env-border bg-env-card p-4 text-center"
          >
            <p className="text-2xl font-bold font-mono text-env-green-400">
              {m.value}
            </p>
            <p className="mt-1 text-xs text-env-text-muted">{m.label}</p>
          </div>
        ))}
      </div>

      {/* Timeline */}
      <div className="rounded-xl border border-env-border bg-env-card p-6">
        <h2 className="mb-6 text-lg font-semibold text-env-text-primary">
          Development Timeline
        </h2>
        <ol className="relative border-l border-env-border space-y-6 pl-6">
          {timeline.map((item) => (
            <li key={item.year} className="relative">
              <div className="absolute -left-[25px] flex h-4 w-4 items-center justify-center rounded-full border border-env-green-500 bg-env-dark">
                <div className="h-1.5 w-1.5 rounded-full bg-env-green-400" />
              </div>
              <p className="font-mono text-xs font-semibold text-env-green-400 mb-1">
                {item.year}
              </p>
              <p className="text-sm text-env-text-secondary">{item.event}</p>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
