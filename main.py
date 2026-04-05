#!/usr/bin/env python3
"""
Bishkek PM2.5 Smog Predictor — CLI
====================================
Usage:
    python main.py train              # ingest history + train CatBoost model
    python main.py predict            # predict PM2.5 for next 5 days
    python main.py predict --days 3   # predict PM2.5 for next 3 days
"""

import argparse
import sys


def cmd_train(args):
    """Ingest historical data and train the CatBoost model."""
    from smog.ingest import run_ingest
    from smog.train import run_train

    print("=" * 60)
    print("  TRAIN MODE — Bishkek PM2.5 Smog Predictor")
    print("=" * 60)

    # Step 1: Ingest
    print("\n📥 Step 1/2: Ingesting data from Open-Meteo …")
    out_path, df_daily = run_ingest(start="2022-08-01")
    print(f"   ✅ Saved {len(df_daily)} rows → {out_path}")

    # Step 2: Train
    print("\n🏋️  Step 2/2: Training CatBoost model …")
    model_path, feats_path, metrics_path, cv_mean, hold = run_train(
        verbose=args.verbose,
    )
    print(f"   ✅ Model   → {model_path}")
    print(f"   ✅ Features → {feats_path}")
    print(f"   ✅ Metrics  → {metrics_path}")

    print("\n📊 Results:")
    print(f"   CV  mean  MAE = {cv_mean['mae']:.3f}  |  RMSE = {cv_mean['rmse']:.3f}  |  R² = {cv_mean['r2']:.3f}")
    print(f"   Holdout   MAE = {hold['mae']:.3f}  |  RMSE = {hold['rmse']:.3f}  |  R² = {hold['r2']:.3f}")
    print("\n🎉 Training complete!")


def cmd_predict(args):
    """Fetch weather forecast and predict PM2.5 for the next N days."""
    from smog.predict import run_predict

    print("=" * 60)
    print("  PREDICT MODE — Bishkek PM2.5 Forecast")
    print("=" * 60)

    results = run_predict(days=args.days)

    print(f"\n{'─' * 44}")
    print(f"  {'Date':<14} {'PM2.5':>7}  {'Status'}")
    print(f"{'─' * 44}")

    for r in results:
        print(f"  {r['date']:<14} {r['pm25']:>6.1f}  {r['status']}")

    print(f"{'─' * 44}")
    print(f"\n🏙️  Location: Bishkek (42.87°N, 74.59°E)")
    print(f"📅 Forecast days: {args.days}")
    print(f"💡 Unit: µg/m³ (daily mean PM2.5)")


def main():
    parser = argparse.ArgumentParser(
        prog="smog-predictor",
        description="🌫️ Bishkek PM2.5 Smog Predictor — Train or Predict",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── train ─────────────────────────────────────────────────────────────
    train_parser = subparsers.add_parser(
        "train",
        help="Ingest historical data and train the CatBoost model",
    )
    train_parser.add_argument(
        "--verbose", "-v",
        type=int,
        default=100,
        help="CatBoost verbose interval (default: 100)",
    )
    train_parser.set_defaults(func=cmd_train)

    # ── predict ───────────────────────────────────────────────────────────
    predict_parser = subparsers.add_parser(
        "predict",
        help="Predict PM2.5 for the next N days using weather forecast",
    )
    predict_parser.add_argument(
        "--days", "-d",
        type=int,
        default=5,
        help="Number of forecast days (default: 5, max: 16)",
    )
    predict_parser.set_defaults(func=cmd_predict)

    # ── parse & dispatch ──────────────────────────────────────────────────
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
