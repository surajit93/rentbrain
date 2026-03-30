class DecisionEngine:
    def decision(self, salary, rent, effective_tax=0.22, fixed_costs=1480):
        net=(salary/12)*(1-effective_tax)
        post_rent=net-rent-fixed_costs
        status="safe" if post_rent>=500 else "tight" if post_rent>=0 else "risky"
        return {"monthly_net":round(net,2),"post_rent_cash":round(post_rent,2),"status":status}
