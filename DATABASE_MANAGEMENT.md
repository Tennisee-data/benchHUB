# Database Management Guide

This guide covers database administration for the benchHUB leaderboard system.

## Overview

The benchHUB leaderboard uses:
- **Production**: PostgreSQL database on Render.com
- **Development**: Local SQLite database
- **Auto-detection**: Uses `DATABASE_URL` environment variable

## Database Manager Tool

The `db_manager.py` script provides comprehensive database administration capabilities.

### Prerequisites

```bash
# Ensure you have the required dependencies
pip install -r requirements-api.txt
```

### Environment Setup

**For Production (Render.com):**
```bash
# DATABASE_URL is automatically set by Render
# No additional setup required
```

**For Local Development:**
```bash
# Will automatically use local SQLite: leaderboard.db
# No environment variables needed
```

## Available Commands

### 1. Database Statistics

Show current database state and score distribution:

```bash
python db_manager.py stats
```

**Output includes:**
- Total number of results
- Results per configuration (light, standard, heavy)
- Score ranges and averages
- Distribution analysis (zero scores, valid scores, outliers)

### 2. Clear Zero Scores

Remove invalid submissions with zero or negative scores:

```bash
python db_manager.py clear-zero
```

**Use case:** Clean up broken submissions from before the scoring bug fix.

### 3. Clear High Scores

Remove scores above a threshold (old scoring system):

```bash
python db_manager.py clear-high --threshold 1000
```

**Use case:** Remove results from before the scoring formula was adjusted.

**Options:**
- `--threshold N`: Set custom threshold (default: 1000)

### 4. Limit Scores Per Category

Keep only the top N scores for each configuration:

```bash
python db_manager.py limit --limit 2000
```

**Use case:** Maintain database performance and relevance.

**Options:**
- `--limit N`: Number of top scores to keep (default: 2000)

### 5. Clear All Data (Nuclear Option)

Remove all benchmark results:

```bash
python db_manager.py clear-all
```

⚠️ **WARNING:** This permanently deletes ALL data. Requires explicit confirmation.

## Recommended Maintenance Workflow

### After Scoring System Changes

When the scoring formula is updated, follow this sequence:

1. **Assess current state:**
   ```bash
   python db_manager.py stats
   ```

2. **Remove broken submissions:**
   ```bash
   python db_manager.py clear-zero
   ```

3. **Remove old scoring results:**
   ```bash
   python db_manager.py clear-high --threshold 1000
   ```

4. **Verify cleanup:**
   ```bash
   python db_manager.py stats
   ```

5. **Limit database size (optional):**
   ```bash
   python db_manager.py limit --limit 2000
   ```

### Regular Maintenance

**Monthly cleanup:**
```bash
# Keep database lean and relevant
python db_manager.py limit --limit 5000
```

**Performance monitoring:**
```bash
# Check database health
python db_manager.py stats
```

## Score Ranges Guide

### Current Scoring System (v1.0.1+)
- **Light profile**: 200-600 points
- **Standard profile**: 400-800 points  
- **Heavy profile**: 600-999 points (capped)

### Legacy Scoring Issues
- **Zero scores**: Broken submissions (pre-fix)
- **>1000 scores**: Old scoring formula (pre-adjustment)
- **>10,000 scores**: Very old scoring system

## Safety Features

### Confirmation Requirements
- **Clear operations**: Require explicit user confirmation
- **Production warnings**: Extra warnings for production database
- **Count display**: Shows exactly how many records will be affected

### Non-destructive Operations
- `stats`: Read-only, safe to run anytime
- **Dry-run capability**: Always shows counts before deletion

### Error Handling
- **Connection failures**: Graceful error messages
- **SQL errors**: Detailed error reporting
- **Rollback protection**: Uses database transactions

## Production Deployment

### On Render.com

The script automatically detects the production environment via `DATABASE_URL`.

**To run maintenance:**

1. **Via Render Console:**
   - Go to your benchhub-api service
   - Open "Console" tab
   - Run commands directly

2. **Via Local Connection:**
   ```bash
   # Set production database URL locally
   export DATABASE_URL="postgresql://username:password@host:port/database"
   python db_manager.py stats
   ```

### Backup Recommendations

**Before major operations:**
1. Use Render's database backup feature
2. Export current data if needed
3. Test operations on development database first

## Troubleshooting

### Common Issues

**"No DATABASE_URL found"**
- Normal for local development
- Uses SQLite automatically

**"Connection failed"**
- Check DATABASE_URL format
- Verify network connectivity
- Confirm database service is running

**"Permission denied"**
- Ensure database user has required permissions
- Check Render service status

**"No results found"**
- Database might be empty
- Check if API service is receiving submissions

### Getting Help

1. Run `python db_manager.py stats` to diagnose
2. Check API service logs on Render
3. Verify benchmark submission process
4. Review recent code changes

## Security Notes

- **Production access**: Only authorized administrators should run cleanup commands
- **Environment isolation**: Always verify which database you're connecting to
- **Audit trail**: Record major database operations
- **Regular backups**: Use Render's automated backup features

## Contributing

When adding new database management features:

1. Add appropriate safety checks
2. Include confirmation prompts for destructive operations
3. Provide clear error messages
4. Update this documentation
5. Test on development database first