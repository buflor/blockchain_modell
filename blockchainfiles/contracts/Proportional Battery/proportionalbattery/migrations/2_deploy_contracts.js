const propBat = artifacts.require("proportionalBattery");

module.exports = function(deployer) {
  deployer.deploy(propBat, 10000, 30000);
};
