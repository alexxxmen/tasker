# -*- coding:utf-8 -*-

from tasker import app

if __name__ == "__main__":
    print 'starting roller'
    app.run(debug=False, host="0.0.0.0", port=5120)
