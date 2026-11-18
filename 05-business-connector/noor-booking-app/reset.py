"""Wipe bookings.db and reload the synthetic fixture. Run before every capture run."""
import seed

if __name__ == "__main__":
    seed.build(force=True)
