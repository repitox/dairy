# Dashboard Loading - Debug & Testing Guide

## 🎯 Quick Check: Is Your Dashboard Optimized?

### Step 1: Open Browser DevTools
```
Chrome/Edge: Press F12
Firefox: Press F12
Safari: Cmd + Option + I
```

### Step 2: Go to Console Tab
Look for these messages when loading dashboard:

✅ **You should see:**
```
📊 Начало загрузки данных дашборда для пользователя: 2
⏱️ Загрузка задач: 145.32ms
✅ Задачи загружены: {overdue: Array(0), today: Array(3)}
⏱️ Загрузка событий: 120.15ms
✅ События загружены: [...]
⏱️ Загрузка покупок: 158.47ms
✅ Покупки загружены: [...]
⏱️ Загрузка заметок: 134.89ms
✅ Заметки загружены: [...]
```

This confirms **independent parallel loading** is working!

---

## 🔍 Performance Verification

### Method 1: Network Tab Analysis

1. **Open DevTools → Network Tab**
2. **Reload Page** (Ctrl+R)
3. **Look for these requests:**
   - `tasks/today` - should start immediately
   - `events/today` - should start immediately  
   - `shopping` - should start immediately
   - `notes` - should start immediately

✅ **Correct**: All 4 requests show same start time (~0ms difference)
❌ **Wrong**: Requests start one after another

### Method 2: Request Waterfall View

**Good (Parallel):**
```
tasks     ├─────────────────┤
events    ├──────────────────┤
shopping  ├─────────────────────┤
notes     ├────────────────────┤
```

**Bad (Sequential):**
```
tasks     ├─────────────────┤
events              ├──────────────────────┤
shopping                      ├─────────────────────┤
notes                                    ├────────────────────┤
```

---

## 🚀 Real-Time Performance Testing

### Test 1: Monitor Actual Load Times

**In Console, paste:**
```javascript
// This will show you actual rendering times for each section
const sections = ['tasks', 'events', 'shopping', 'notes'];
sections.forEach(section => {
    const time = performance.measure(`dashboard-${section}`)?.duration;
    console.log(`${section}: ${time?.toFixed(2)}ms`);
});
```

### Test 2: Simulate Slow Network

1. **DevTools → Network Tab**
2. **Find dropdown that says "No throttling"**
3. **Select "Slow 3G" or "Fast 3G"**
4. **Reload Page**

Observe:
- Loading spinners appear for each section
- Sections render as they become ready (not all at once)
- Total time is sum of slowest endpoint, not all endpoints

### Test 3: Simulate Network Errors

1. **DevTools → Network Tab**
2. **Find your API request (e.g., `tasks/today`)**
3. **Right-click → Block URL**
4. **Reload Page**

Result: Other sections load fine, blocked section shows empty state gracefully

---

## 📊 Docker Logs Analysis

### View Real-Time Logs

```bash
# Watch live logs
docker logs -f tg_project-app-new-1

# View last 50 lines
docker logs tg_project-app-new-1 | tail -50

# View logs from specific time
docker logs tg_project-app-new-1 --since 10m
```

### What to Look For

```
✅ Good - All requests complete successfully:
GET /api/tasks/today?user_id=2 → 200 OK
GET /api/events/today?user_id=2 → 200 OK
GET /api/shopping?user_id=2 → 200 OK
GET /api/notes?user_id=2&limit=5 → 200 OK

❌ Bad - Request fails:
GET /api/tasks/today?user_id=2 → 500 ERROR
```

---

## 🐢 Testing Slow API Response

### Temporarily Make API Slow (for testing)

**Edit** `/Users/d.dubenetskiy/Documents/tg_project/app/api/tasks.py`:

```python
@router.get("/tasks/today")
async def get_today_tasks(user_id: int):
    import asyncio
    await asyncio.sleep(3)  # Simulate 3 second delay
    # ... rest of function
```

Then reload dashboard to see the effect:
- Tasks section loads after 3 seconds
- Other sections load normally
- Total time = ~3 seconds (not sum of all!)

**Remember to remove the delay after testing!**

---

## 🔧 Common Issues & Solutions

### Issue 1: Dashboard Shows Blank/No Data

**Diagnostics:**
1. Open Console (F12)
2. Look for error messages starting with ❌
3. Check Network tab for failed requests (red color)

**Solution:**
- Check if you're logged in: `localStorage.getItem('telegram_user')`
- Check if user_id is correct: `console.log(Auth.getCurrentUserId())`
- Verify Docker container is running: `docker ps`
- Check API logs: `docker logs tg_project-app-new-1`

### Issue 2: One Section Stuck on Loading

**Cause**: Specific API endpoint is slow or error

**Check:**
```javascript
// In console, check which endpoint is slow:
// Look in Network tab for red (error) or long time (slow)
```

**Solution:**
- Check Docker API logs for errors
- Verify database has data for that section
- Check network connection (throttle in DevTools)

### Issue 3: Dashboard Takes 30+ Seconds

**Cause**: Likely database issue or network problem

**Diagnostics:**
1. Open Network tab in DevTools
2. Look at response time for each endpoint
3. If one takes 30s, that's the bottleneck

**Solutions:**
```bash
# Check database connection
docker logs tg_project-db-1 | tail -20

# Check if app can reach database
docker exec tg_project-app-new-1 psql -h db -U postgres -d telegram_app -c "SELECT 1"

# Monitor database performance
docker stats tg_project-db-1
```

---

## 📈 Performance Benchmarks

### Expected Times (Local Docker)

| Scenario | Time | Status |
|----------|------|--------|
| Fast network, cached | 0.5-1s | ✅ Excellent |
| Normal network | 1-2s | ✅ Good |
| Slow 3G simulation | 5-10s | ✅ Acceptable |
| 1 slow endpoint | 2-5s | ✅ Progressive |

### Red Flags (Indicates Problem)

| Time | Issue | Action |
|------|-------|--------|
| > 30s | Very slow | Check Docker logs |
| Sequential loading | Not parallel | Code issue |
| All endpoints fail | Network issue | Check firewall/Docker |
| Some endpoints fail | Partial issue | Check specific API |

---

## 🧪 Automated Health Check

### Create Health Check Script

**Save as `check_dashboard_perf.sh`:**

```bash
#!/bin/bash

API_URL="http://localhost:8000/api"
USER_ID=2

echo "🔍 Dashboard Performance Check"
echo "=============================="

# Test each endpoint
endpoints=("tasks/today" "events/today" "shopping" "notes?limit=5")

for endpoint in "${endpoints[@]}"; do
    echo ""
    echo "Testing: $endpoint"
    
    # Measure response time
    start_time=$(date +%s%N | cut -b1-13)
    
    response=$(curl -s -w "\n%{http_code}" "$API_URL/$endpoint?user_id=$USER_ID")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    end_time=$(date +%s%N | cut -b1-13)
    duration=$((end_time - start_time))
    
    if [ "$http_code" = "200" ]; then
        echo "✅ HTTP $http_code | Response: ${duration}ms"
        echo "Data: $(echo $body | jq -r 'if type=="array" then "Array: \(length) items" elif type=="object" then "Object: \(keys)" else . end')"
    else
        echo "❌ HTTP $http_code | Response: ${duration}ms"
        echo "Error: $body"
    fi
done

echo ""
echo "✅ Check complete!"
```

**Run it:**
```bash
chmod +x check_dashboard_perf.sh
./check_dashboard_perf.sh
```

---

## 📱 Mobile Testing

### Check Responsive Loading

1. **Open DevTools → Toggle device toolbar** (Ctrl+Shift+M)
2. **Select iPhone 12 or similar**
3. **Reload Dashboard**
4. **Observe:**
   - Navigation collapses properly
   - Sections stack vertically
   - Loading still works correctly
   - No horizontal scrolling

---

## 🔐 Security Check

### Verify User Data is Secure

1. **Console:**
   ```javascript
   // Check localStorage doesn't expose sensitive data
   Object.keys(localStorage).forEach(key => {
       console.log(`${key}: ${localStorage.getItem(key)}`)
   });
   ```

2. **Network Tab:**
   - All API calls should be over HTTPS in production
   - No passwords in URLs
   - user_id is the only identifier passed

---

## 🎓 Console Command Reference

### Quick Diagnostic Commands

```javascript
// Check if user is logged in
Auth.isAuthenticated()  // true/false

// Get current user ID
Auth.getCurrentUserId()  // Returns database ID

// Get full user object
Auth.getCurrentUser()  // Returns {id, first_name, telegram_id, ...}

// Validate user on server
await Auth.validateUserOnServer()  // true/false

// Manually reload dashboard data
loadDashboardData(2)  // Reloads all sections

// Check API response
fetch('/api/tasks/today?user_id=2').then(r => r.json()).then(d => console.log(d))

// Simulate logout
Auth.logout()  // Clears all data and redirects
```

---

## 📞 Troubleshooting Checklist

Before reporting an issue, verify:

- [ ] Browser DevTools Console shows no errors (❌ messages)
- [ ] Docker containers are running: `docker ps`
- [ ] User is logged in: `Auth.isAuthenticated()` returns true
- [ ] Network tab shows 200 OK for all 4 endpoints
- [ ] Page loaded within 10 seconds on normal network
- [ ] All 4 requests are in parallel (same start time)
- [ ] Each section has correct data type (array, object, etc.)
- [ ] Empty sections show empty state message (not error)

---

## 🚀 Advanced: Profiling with Performance API

### Detailed Performance Profile

```javascript
// Add this to main.html before loadDashboardData()

const perfStart = performance.now();

window.loadDashboardData = (function(original) {
    return async function(userId) {
        const sectionStart = {
            tasks: performance.now(),
            events: performance.now(),
            shopping: performance.now(),
            notes: performance.now()
        };
        
        // Call original function
        const result = await original.call(this, userId);
        
        // Log detailed timing
        console.table({
            'Total Time': performance.now() - perfStart,
            'Tasks': performance.now() - sectionStart.tasks,
            'Events': performance.now() - sectionStart.events,
            'Shopping': performance.now() - sectionStart.shopping,
            'Notes': performance.now() - sectionStart.notes
        });
        
        return result;
    };
})(loadDashboardData);
```

---

## 📋 Reporting Performance Issues

When reporting dashboard is slow, include:

1. **Console Output** (F12 → Console)
   - Screenshot or copy of logs
   
2. **Network Timings** (F12 → Network)
   - Response times for each endpoint
   - Total page load time
   
3. **System Info**
   - Browser and version
   - OS (Windows/Mac/Linux)
   - Network speed (throttled or real?)
   
4. **Docker Status**
   ```bash
   docker ps
   docker logs tg_project-app-new-1 | tail -50
   docker stats
   ```

---

## ✅ Success Criteria

Dashboard loading is **optimized** when:

✅ All 4 API requests start in parallel
✅ Each section renders as data arrives
✅ Total load time = slowest endpoint (~1-2s)
✅ Console shows individual endpoint timings
✅ No cascading spinner effects
✅ Empty states appear gracefully if endpoint fails
✅ Network tab shows 4 concurrent requests

---

**Last Updated**: 2025-01-22  
**Version**: 1.0  
**Status**: ✅ Production Ready