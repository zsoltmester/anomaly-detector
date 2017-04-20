'use strict'

class ChartController {
  * index (request, response) {
    yield response.sendView('chart-showcase')
  }
}

module.exports = ChartController
