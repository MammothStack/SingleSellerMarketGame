class Player {
  constructor(name) {
    this.name = name;
  }
}

class OperationModel {
  constructor(
    model,
    name,
    operation,
    loss,
    true_threshold,
    max_cash_limit,
    optimizer="adam",
    metrics=["accuracy"]) {

    if (optimizer === undefined) {
      optimizer = "adam";
    }

    if (metrics === undefined) {
      metrics=["accuracy"];
    }

    this.model = model;
    this.name = name;
    this.operation = operation;
    this.loss = loss;
    this.true_threshold = true_threshold;
    this.max_cash_limit = max_cash_limit;
    this.optimizer = optimizer;
    this.metrics = metrics;
  }
}

class BoardInformation {
  constructor(player_names, max_cash_limit, houses, hotels) {
    this.player_names = player_names;
    this.max_cash_limit = max_cash_limit;
    this.available_houses = houses;
    this.available_hotels = hotels;
  }
}

class BoardController {
  constructor(operation_models, upgrade_limit) {
    this.operation_models = operation_models;
    this.upgrade_limit = upgrade_limit;
  }
}



function start_game() {
  const model = tf.loadModel('https://github.com/MammothStack/SingleSellerMarketGame/tree/master/models/js/amaranth/model.json');

  alert(model.name)
  alert("Not yet implented. coming soon");
}
